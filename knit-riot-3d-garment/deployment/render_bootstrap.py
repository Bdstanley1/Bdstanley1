import os,re,runpy,subprocess,tempfile
from pathlib import Path
commit=os.environ['KR_PROJECT_COMMIT']
if not re.fullmatch(r'[0-9a-f]{40}',commit):raise RuntimeError('A full pinned project commit is required')
output=Path.cwd()/'public'
with tempfile.TemporaryDirectory(prefix='knit-riot-source-') as temp:
 root=Path(temp)/'project'
 subprocess.run(['git','clone','--no-checkout','--depth','1','https://github.com/Bdstanley1/Bdstanley1.git',str(root)],check=True,timeout=180)
 subprocess.run(['git','-C',str(root),'fetch','--depth','1','origin',commit],check=True,timeout=180)
 subprocess.run(['git','-C',str(root),'checkout','--detach',commit],check=True,timeout=60)
 actual=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
 if actual!=commit:raise RuntimeError('Project commit verification failed')
 os.environ['KR_PUBLISH_DIR']=str(output.resolve())
 runpy.run_path(str(root/'knit-riot-3d-garment/tools/render_build.py'),run_name='__main__')
