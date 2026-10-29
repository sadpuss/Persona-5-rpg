from pathlib import Path
import importlib.util,os,tempfile,shutil,sys
import pypdfium2 as pdfium
from PIL import Image,ImageOps,ImageDraw
R=Path(__file__).parent;Q=R/'qa_balance_update';(Q/'temp').mkdir(exist_ok=True)
os.environ['TEMP']=os.environ['TMP']=str(Q/'temp');tempfile.tempdir=str(Q/'temp')
p=Path('C:/Users/magda/.codex/plugins/cache/openai-primary-runtime/documents/26.1025.11240/skills/documents/render_docx.py');spec=importlib.util.spec_from_file_location('doc_renderer',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for name,doc in [('player','Persona_5_RPG_Podrecznik_Gracza_0_5.docx'),('gm','Persona_5_RPG_Podrecznik_GM_0_8.docx'),('bestiary','Persona_5_RPG_Bestiariusz_0_5.docx')]:
 if len(sys.argv)>1 and name not in sys.argv[1:]:continue
 pdf=Q/(name+'.pdf');out=Q/name;out.mkdir(exist_ok=True)
 m.convert_to_pdf=lambda *args,**kwargs:(str(pdf),'PDF wyeksportowany przez Microsoft Word; brak LibreOffice w środowisku Windows.')
 def convert(pdf_path,output_folder,**kwargs):
  paths=[]
  with pdfium.PdfDocument(pdf_path) as d:
   for i,page in enumerate(d):
    dest=Path(output_folder)/f'page0001-{i+1:03}.png';page.render(scale=1.25).to_pil().save(dest);page.close();paths.append(str(dest))
  return paths
 m.convert_from_path=convert
 paths=m.rasterize(str(R/doc),str(out),90,False,False)

 for start in range(0,len(paths),8):
  sheet=Image.new('RGB',(1600,2300),'#dddddd');draw=ImageDraw.Draw(sheet)
  for j,path in enumerate(paths[start:start+8]):
   im=Image.open(path);im.thumbnail((790,540));x=(j%2)*800+(800-im.width)//2;y=(j//2)*575+25;sheet.paste(im,(x,y));draw.text(((j%2)*800+10,(j//2)*575+5),f'{name} strona {start+j+1}',fill='black')
  sheet.save(Q/f'{name}-arkusz-{start//8+1}.jpg')
 print(name,len(paths),'pages',flush=True)
