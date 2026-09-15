#!/usr/bin/env python3
"""Native CLI process-boundary regressions. Never makes provider calls."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ask_cli', ROOT / 'scripts/ask-cli.py')
ask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ask)

FAKE = '''#!/usr/bin/env python3
import json,os,sys,time
from pathlib import Path
args=sys.argv[1:]
if args == ['inspect','--json']:
 print(json.dumps({'skills':[], 'plugins':[]}));sys.exit(0)
if args == ['list']:
 print('NAME ID SIZE MODIFIED\\nfixture:local abc 1GB now');sys.exit(0)
prompt=sys.stdin.read()
Path(os.environ['CAPTURE']).write_text(json.dumps({'args':args,'prompt':prompt,'cwd':os.getcwd(),
 'grok_config':Path(os.environ['GROK_HOME'],'config.toml').read_text() if os.environ.get('GROK_HOME') else None,
 'env':{k:v for k,v in os.environ.items() if k.startswith(('ANTHROPIC_', 'ZAI_', 'ASK_GATEWAY_', 'CLAUDE_', 'GROK_', 'DREAMER_'))}}))
if os.environ.get('SLEEP'): time.sleep(10)
if os.environ.get('FAIL'):
 print(os.environ['FAIL'],file=sys.stderr);sys.exit(1)
if args[0]=='run': print('fixture answer');sys.exit(0)
print(os.environ.get('RESPONSE',json.dumps({'result':'fixture answer','modelUsage':{'claude-opus-example':{'inputTokens':1}},'usage':{'input_tokens':1}})))
'''

class NativeAskTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fake = self.root / 'cli'
        self.fake.write_text(FAKE)
        self.fake.chmod(0o755)
        self.capture = self.root / 'capture'
        self.env = os.environ.copy()
        self.env.update(HOME=str(self.root), CRAFT_ASK_ENV=str(self.root / 'absent'), CAPTURE=str(self.capture))
        for route in ask.PROVIDERS:
            self.env[f'ASK_{route.upper()}_CLI'] = str(self.fake)
        for key in ('ZAI_API_KEY', 'ZAI_API_KEY_FILE', 'ASK_DEFAULT_PROVIDER', 'ASK_TIMEOUT', 'ASK_CLAUDE_MODEL', 'ASK_GROK_MODEL', 'ASK_ZAI_MODEL', 'ASK_OLLAMA_MODEL'):
            self.env.pop(key, None)

    def run_ask(self,*args,prompt='Question'):
        return subprocess.run([str(ROOT/'scripts/ask.sh'),*args],input=prompt,text=True,capture_output=True,env=self.env,timeout=15)

    def test_symlink_entry_point_resolves_bundled_python(self):
        link=self.root/'craft-ask'
        link.symlink_to(ROOT/'scripts/ask.sh')
        result=subprocess.run([str(link),'--list','--json'],text=True,capture_output=True,env=self.env)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(json.loads(result.stdout)['routes']),4)

    def test_legacy_routes_are_rejected_without_api_fallback(self):
        for route in ('luna','openai','gpt'):
            with self.subTest(route=route):
                result=self.run_ask(route,'-')
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertFalse(self.capture.exists())

    def test_list_four_native_routes_no_inference(self):
        result=self.run_ask('--list','--json')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual([x['provider'] for x in json.loads(result.stdout)['routes']],['claude','grok','zai','ollama'])
        self.assertFalse(self.capture.exists())

    def test_prompt_is_stdin_tools_disabled_and_secrets_isolated(self):
        prompt='Quote "this"\nΩ $(touch sentinel)'
        self.env.update(ZAI_API_KEY='zai-secret',ASK_GATEWAY_KEY='gateway-secret',DREAMER_API_KEY='other-secret',ANTHROPIC_BASE_URL='https://wrong.invalid')
        result=self.run_ask('--json','claude','-',prompt=prompt)
        self.assertEqual(result.returncode,0,result.stderr)
        capture=json.loads(self.capture.read_text())
        self.assertEqual(capture['prompt'],prompt)
        self.assertNotIn(prompt,capture['args'])
        self.assertEqual(capture['args'][capture['args'].index('--tools')+1],'')
        self.assertIn('--strict-mcp-config',capture['args'])
        self.assertIn('--no-session-persistence',capture['args'])
        self.assertNotIn('ZAI_API_KEY',capture['env'])
        self.assertNotIn('ASK_GATEWAY_KEY',capture['env'])
        self.assertNotIn('DREAMER_API_KEY',capture['env'])
        self.assertEqual(capture['env']['ANTHROPIC_BASE_URL'],'https://api.anthropic.com')
        self.assertFalse(Path(capture['cwd']).exists())
        payload=json.loads(result.stdout)
        self.assertEqual(payload['model'],'claude-opus-example')
        self.assertEqual(payload['requested_model'],'opus')
        self.assertEqual(payload['provenance'],'cli-reported')

    def test_zai_uses_ephemeral_config_and_private_key_file(self):
        key=self.root/'zai.key';key.write_text('zai-secret');key.chmod(0o600)
        self.env.update(ZAI_API_KEY_FILE=str(key),CLAUDE_CODE_OAUTH_TOKEN='anthropic-secret',RESPONSE=json.dumps({'result':'answer','model':'glm-5.3'}))
        result=self.run_ask('--json','zai','-')
        self.assertEqual(result.returncode,0,result.stderr)
        capture=json.loads(self.capture.read_text())
        self.assertEqual(capture['env']['ANTHROPIC_AUTH_TOKEN'],'zai-secret')
        self.assertEqual(capture['env']['ANTHROPIC_BASE_URL'],'https://api.z.ai/api/anthropic')
        self.assertNotIn('CLAUDE_CODE_OAUTH_TOKEN',capture['env'])
        self.assertFalse(Path(capture['env']['CLAUDE_CONFIG_DIR']).exists())
        self.assertNotIn('zai-secret',result.stdout+result.stderr+' '.join(capture['args']))

    def test_missing_zai_key_does_not_invoke_cli(self):
        result=self.run_ask('zai','-')
        self.assertEqual(result.returncode,3,result.stderr)
        self.assertFalse(self.capture.exists())

    def test_missing_cli_does_not_fallback_to_gateway(self):
        self.env.update(ASK_GROK_CLI='/absent/grok',ASK_GATEWAY_URL='https://fixture.invalid',ASK_GATEWAY_KEY='secret')
        result=self.run_ask('grok','-')
        self.assertEqual(result.returncode,4,result.stderr)
        self.assertFalse(self.capture.exists())

    def test_ollama_is_requested_only_no_automatic_pull(self):
        result=self.run_ask('ollama','-')
        self.assertEqual(result.returncode,4,result.stderr)
        self.assertFalse(self.capture.exists())
        self.env['ASK_OLLAMA_MODEL']='fixture:local'
        result=self.run_ask('--json','ollama','-')
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout)
        self.assertIsNone(data['model'])
        self.assertEqual(data['requested_model'],'fixture:local')
        self.assertEqual(data['provenance'],'requested-only')
        self.assertEqual(json.loads(self.capture.read_text())['args'][0],'run')

    def test_ollama_absent_named_model_never_invokes_run(self):
        self.env['ASK_OLLAMA_MODEL']='not-installed:latest'
        result=self.run_ask('ollama','-')
        self.assertEqual(result.returncode,4,result.stderr)
        self.assertIn('refusing automatic pull',result.stderr)
        self.assertFalse(self.capture.exists())

    def test_grok_no_tools_and_missing_identity_is_explicit(self):
        self.env['RESPONSE']=json.dumps({'result':'answer'})
        result=self.run_ask('--json','grok','-')
        self.assertEqual(result.returncode,0,result.stderr)
        args=json.loads(self.capture.read_text())['args']
        self.assertEqual(args[args.index('--tools')+1],'__craft_no_tools__')
        capture=json.loads(self.capture.read_text())
        self.assertIn('[plugins]',capture['grok_config'])
        self.assertEqual(capture['env']['GROK_CLAUDE_HOOKS_ENABLED'],'false')
        self.assertEqual(capture['env']['GROK_CURSOR_MCPS_ENABLED'],'false')
        self.assertFalse(Path(capture['env']['GROK_HOME']).exists())
        for flag in ('--no-subagents','--disable-web-search','--verbatim','--deny'):
            self.assertIn(flag,args)
        self.assertEqual(json.loads(result.stdout)['provenance'],'requested-only')

    def test_real_grok_json_envelope_model_usage(self):
        self.env['RESPONSE']=json.dumps({'text':'OK','stopReason':'end_turn','modelUsage':{'grok-4.6-build':{'modelCalls':1}},'usage':{'total_tokens':4}})
        result=self.run_ask('--json','grok','-')
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout)
        self.assertEqual(data['content'],'OK')
        self.assertEqual(data['model'],'grok-4.6-build')
        self.assertEqual(data['provenance'],'cli-reported')

    def test_exact_model_mismatch_rejected(self):
        result=self.run_ask('claude','--model','exact-model','-')
        self.assertEqual(result.returncode,7,result.stderr)

    def test_malformed_and_empty_output(self):
        for response in ('garbage','[]','{}','{"result":""}'):
            with self.subTest(response=response):
                self.env['RESPONSE']=response
                result=self.run_ask('claude','-')
                self.assertEqual(result.returncode,7,result.stderr)

    def test_errors_classified_without_echoing_secrets(self):
        for error,code in [('401 secret-token',3),('quota secret-token',5),('unknown model secret-token',4),('service failed secret-token',6)]:
            self.env['FAIL']=error
            result=self.run_ask('grok','-')
            self.assertEqual(result.returncode,code,result.stderr)
            self.assertNotIn('secret-token',result.stdout+result.stderr)

    def test_timeout_terminates_and_cleans_scratch(self):
        self.env.update(SLEEP='1',ASK_TIMEOUT='0.7')
        result=self.run_ask('grok','-')
        self.assertEqual(result.returncode,6,result.stderr)
        self.assertFalse(Path(json.loads(self.capture.read_text())['cwd']).exists())

    def test_auth_refresh_does_not_replace_concurrent_native_update(self):
        original=self.root/'auth.json';original.write_text('{"token":"old"}');original.chmod(0o600)
        copied=self.root/'copied.json';copied.write_text('{"token":"new"}')
        state=(original, original.read_bytes(), copied)
        original.write_text('{"token":"concurrent"}')
        ask.preserve_grok_auth(state)
        self.assertEqual(json.loads(original.read_text())['token'],'concurrent')

    def test_private_config_does_not_execute_shell(self):
        config=self.root/'ask.env';config.write_text('ASK_GROK_MODEL=fixture\nPATH=/absent\nBASH_ENV=/absent\n');config.chmod(0o600)
        self.env['CRAFT_ASK_ENV']=str(config)
        self.env['RESPONSE']=json.dumps({'result':'answer','model':'fixture'})
        result=self.run_ask('--json','grok','-')
        self.assertEqual(result.returncode,0,result.stderr)
        config.chmod(0o644)
        result=self.run_ask('--status')
        self.assertEqual(result.returncode,3,result.stderr)

if __name__=='__main__':unittest.main()
