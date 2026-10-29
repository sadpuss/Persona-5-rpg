const {_electron:electron}=require('playwright-core');
const fs=require('node:fs/promises');
const path=require('node:path');
const assert=require('node:assert/strict');

(async()=>{
 const output=path.resolve(__dirname,'../qa-desktop');await fs.mkdir(output,{recursive:true});
 const profile=await fs.mkdtemp(path.join(output,'profil-'));
 const env={...process.env,PERSONA_TEST_DATA:profile};delete env.ELECTRON_RUN_AS_NODE;
 const packaged=process.argv.includes('--packaged');
 const executablePath=packaged?path.resolve(__dirname,'../release/win-unpacked/Take Your Heart.exe'):require('electron');
 let app;
 async function launch(){return electron.launch({executablePath,args:packaged?[]:[path.resolve(__dirname,'..')],env});}
 try{
  console.log('Uruchamianie Electron…');
  app=await launch();let page=await app.firstWindow();page.setDefaultTimeout(15000);await page.getByLabel('Imię i nazwisko').waitFor();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.getByLabel('Imię i nazwisko').fill('Maja Kowalska');await page.getByLabel('Pseudonim',{exact:true}).fill('Echo');
  await page.screenshot({path:path.join(output,'kreator-electron.png'),fullPage:true});
  await page.getByRole('button',{name:'02 Arkana'}).click();await page.getByRole('button',{name:/Rydwan/}).click();
  await page.getByRole('button',{name:'03 Twoja Persona'}).click();await page.getByLabel('Nazwa Persony').fill('Latarnik');
  await page.getByLabel('Słabość',{exact:true}).selectOption('Ice');await page.getByLabel('Odporność',{exact:true}).selectOption('Fire');
  await page.getByRole('button',{name:'04 Umiejętności'}).click();await page.getByText('Pomóż mi wybrać — zestawy startowe',{exact:true}).click();await page.getByRole('button',{name:'Ogień i wiatr',exact:true}).click();
  await page.getByRole('button',{name:'05 Rozwój i zasoby'}).click();await page.getByLabel('Zacznij na wybranym poziomie').fill('10');await page.getByRole('button',{name:'Rozpocznij grę'}).click();
  await page.getByLabel('Aktualne HP').fill('12');await page.getByLabel('EXP przyznany przez GM').fill('1000');await page.getByRole('button',{name:'Dodaj EXP'}).click();
  await page.getByLabel('Aktualne HP').filter({visible:true}).waitFor();
  assert.equal(await page.getByLabel('Aktualne HP').inputValue(),'12');
  await page.getByRole('status').filter({hasText:'Zapisano automatycznie'}).waitFor();
  const saved=JSON.parse(await fs.readFile(path.join(profile,'postac.json'),'utf8'));
  console.log('OK: kreator i rozwój.');
  assert.equal(saved.exp,5500);assert.equal(saved.hp,12);assert.equal(saved.skills.length,4);assert.equal(saved.arcana,'Rydwan');
  const characterFile=path.join(output,'test-postaci.json');const pdfFile=path.join(output,'test-kart.pdf');
  await app.evaluate(({dialog},file)=>{dialog.showSaveDialog=async()=>({canceled:false,filePath:file});},characterFile);
  await page.getByRole('button',{name:'Zapisz do pliku'}).click();await page.getByText('Zapisano plik postaci.',{exact:true}).waitFor();
  assert.equal(JSON.parse(await fs.readFile(characterFile,'utf8')).name,'Maja Kowalska');
  await page.getByLabel('Notatki i uzgodnienia z GM').fill('TAJNE_UZGODNIENIE_NIE_DO_DRUKU');
  await page.getByRole('button',{name:'06 Gotowe karty'}).click();
  assert.equal(await page.locator('#print-root .sheet-preview').count(),3);
  assert.equal(await page.locator('#print-root').getByText('TAJNE_UZGODNIENIE_NIE_DO_DRUKU').count(),0);
  assert.equal(await page.locator('#print-root .warning').count(),0);
  await app.evaluate(({dialog},file)=>{dialog.showSaveDialog=async()=>({canceled:false,filePath:file});},pdfFile);
  await page.getByRole('button',{name:'Zapisz PDF'}).click();await page.getByText('Zapisano karty w PDF.',{exact:true}).waitFor();
  assert.ok((await fs.stat(pdfFile)).size>10000);
  console.log('OK: plik postaci i PDF.');
  assert.equal(await page.evaluate(()=>typeof window.require),'undefined');
  assert.equal(await page.evaluate(()=>typeof window.desktop.saveCharacter),'function');
  assert.equal(await page.evaluate(()=>typeof window.desktop.invoke),'undefined');
  console.log('Ponowne uruchomienie…');
  await app.close();app=await launch();page=await app.firstWindow();page.setDefaultTimeout(15000);
  await page.getByLabel('Imię i nazwisko').waitFor();assert.equal(await page.getByLabel('Imię i nazwisko').inputValue(),'Maja Kowalska');
  // Import istniejącego zapisu HTML, potwierdzenie oraz anulowanie systemowego okna.
  await app.evaluate(({dialog},file)=>{dialog.showOpenDialog=async()=>({canceled:false,filePaths:[file]});},characterFile);
  await page.getByRole('button',{name:'Otwórz plik'}).click();await page.getByRole('dialog').waitFor();await page.getByRole('button',{name:'Kontynuuj',exact:true}).click();await page.getByText('Wczytano postać.',{exact:true}).waitFor();
  await app.evaluate(({dialog})=>{dialog.showSaveDialog=async()=>({canceled:true,filePath:undefined});});
  await page.getByRole('button',{name:'Zapisz do pliku'}).click();assert.equal(await page.getByLabel('Imię i nazwisko').inputValue(),'Maja Kowalska');
  assert.deepEqual(errors,[]);
  await fs.writeFile(path.join(output,packaged?'wynik-spakowana.json':'wynik.json'),JSON.stringify({wynik:'OK',spakowana:packaged,kontrole:['okno Electron','React: tworzenie postaci','natywny zapis i import JSON','ponowne uruchomienie i automatyczny zapis','awans bez leczenia','PDF przez Electron','brak ostrzeżeń i uzgodnień w PDF','izolacja Node i preload','anulowanie okna zapisu'],profilTestowy:profile},null,2));
  console.log('OK: aplikacja Electron, zapis/import, awans, PDF i ponowne uruchomienie.');
 }finally{if(app)await app.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
