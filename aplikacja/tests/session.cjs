const {_electron:electron}=require('playwright-core');
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict');

(async()=>{
 const output=path.resolve(__dirname,'../qa-desktop');await fs.mkdir(output,{recursive:true});
 const profile=await fs.mkdtemp(path.join(output,'sesja-'));
 // Zapis sprzed wprowadzenia listy przedmiotów — pole items celowo nie występuje.
 const character={format:1,rulesVersion:'GM 0.8 / Gracz 0.5',name:'Maja Kowalska',alias:'Echo',age:'19',occupation:'Studentka',story:'Szuka zaginionego brata.',arcana:'Rydwan',persona:'Latarnik',concept:'Światło w labiryncie.',image:'',weak:'Ice',resist:'Fire',exp:4500,startLevel:10,skills:[...['Agi','Garu','Dia','Tarunda'].map(name=>({name,source:'start'})),...['Agilao','Garula','Diarama','Maragi'].map(name=>({name,source:'point'}))],spent:4,hp:12,sp:4,bonusHP:0,bonusSP:0,inventory:'Latarka i stary plecak',notes:'Dawna notatka',social:{Wiedza:1,Odwaga:1,Empatia:1,Urok:1,'Zręczność':1},active:true};
 await fs.writeFile(path.join(profile,'postac.json'),JSON.stringify(character));
 const env={...process.env,PERSONA_TEST_DATA:profile};delete env.ELECTRON_RUN_AS_NODE;
 const packaged=process.argv.includes('--packaged'),executablePath=packaged?path.resolve(__dirname,'../release/win-unpacked/Take Your Heart.exe'):require('electron');
 let app;
 const launch=()=>electron.launch({executablePath,args:packaged?[]:[path.resolve(__dirname,'..')],env});
 async function screenshot(page,name){await app.evaluate(({BrowserWindow})=>BrowserWindow.getAllWindows().find(w=>w.webContents.getURL().endsWith('index.html'))?.showInactive());await page.evaluate(()=>scrollTo({top:0,behavior:'instant'}));await page.screenshot({path:path.join(output,name),fullPage:true,animations:'disabled'});}
 try{
  console.log('Sprawdzanie pulpitu prowadzenia postaci…');
  app=await launch();let page=await app.firstWindow();page.setDefaultTimeout(15000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.getByRole('navigation',{name:'Prowadzenie postaci'}).waitFor();
  assert.equal(await page.getByLabel('Aktualne HP').inputValue(),'12');
  await page.getByLabel('Zmiana HP').fill('7');await page.getByRole('button',{name:'− Odejmij HP',exact:true}).click();assert.equal(await page.getByLabel('Aktualne HP').inputValue(),'5');
  await page.getByLabel('Zmiana HP').fill('3');await page.getByRole('button',{name:'＋ Dodaj HP',exact:true}).click();
  await page.getByLabel('Zmiana SP').fill('99');await page.getByRole('button',{name:'− Odejmij SP',exact:true}).click();assert.equal(await page.getByLabel('Aktualne SP').inputValue(),'0');
  await page.getByLabel('Zmiana SP').fill('2');await page.getByRole('button',{name:'＋ Dodaj SP',exact:true}).click();
  await page.getByLabel('EXP przyznany przez GM').fill('1000');await page.getByRole('button',{name:'Dodaj EXP ↗',exact:true}).click();
  assert.equal(await page.getByLabel('Aktualne HP').inputValue(),'8');assert.equal(await page.getByLabel('Aktualne SP').inputValue(),'2');
  await screenshot(page,'pulpit-postaci.png');
  await page.getByRole('button',{name:'02 Umiejętności',exact:true}).click();
  await page.getByLabel('Szukaj nowej umiejętności').fill('Bufula');await page.getByRole('button',{name:'Naucz się Bufu',exact:false}).filter({hasText:'Zastąp'}).click();
  await page.getByRole('dialog').getByLabel('Umiejętność do zastąpienia').selectOption('Garu');
  await page.getByRole('dialog').getByRole('button',{name:'Zastąp i naucz',exact:true}).click();
  assert.equal(await page.getByRole('heading',{name:'Bufula',exact:true}).count(),1);assert.equal(await page.getByRole('heading',{name:'Garu',exact:true}).count(),0);
  await page.getByRole('button',{name:'03 Ekwipunek',exact:true}).click();
  assert.equal(await page.getByLabel('Dodatkowy opis ekwipunku').inputValue(),'Latarka i stary plecak');
  await page.getByLabel('Nazwa przedmiotu', {exact:true}).fill('Lek');await page.getByLabel('Ilość przedmiotu',{exact:true}).fill('3');await page.getByLabel('Opis przedmiotu',{exact:true}).fill('Przywraca 10 HP');
  await page.getByRole('button',{name:'Dodaj przedmiot ↗',exact:true}).click();
  await page.getByLabel('Ilość: Lek',{exact:true}).waitFor();await page.getByRole('button',{name:'Zużyj Lek',exact:true}).click();assert.equal(await page.getByLabel('Ilość: Lek',{exact:true}).inputValue(),'2');
  await screenshot(page,'ekwipunek-postaci.png');
  await page.getByRole('button',{name:'04 Notatki i cechy',exact:true}).click();await page.getByLabel('Notatki i uzgodnienia z GM').fill('PRYWATNY_TROP_SESJI');await page.getByLabel('Wiedza',{exact:true}).fill('2');
  await page.getByRole('button',{name:/Podręczniki/}).click();await page.locator('.manual-entry').last().waitFor();assert.equal(await page.locator('.manual-entry').count(),3);
  const manualFile=path.join(output,'pobrany-podrecznik.docx');await app.evaluate(({dialog},file)=>{dialog.showSaveDialog=async()=>({canceled:false,filePath:file});},manualFile);
  await page.getByRole('button',{name:'Pobierz Podręcznik gracza',exact:true}).click();await page.getByText('Zapisano kopię podręcznika.',{exact:true}).waitFor();
  assert.deepEqual(await fs.readFile(manualFile),await fs.readFile(path.resolve(__dirname,'../../Persona_5_RPG_Podrecznik_Gracza.docx')));
  await app.evaluate(({shell})=>{shell.openPath=async file=>{globalThis.__manualOpened=file;return '';};});
  await page.getByRole('button',{name:'Otwórz Podręcznik gracza',exact:true}).click();await page.getByText('Otwarto dokument w domyślnym programie do plików Word.',{exact:true}).waitFor();
  assert.equal(await app.evaluate(()=>globalThis.__manualOpened),path.resolve(__dirname,'../../Persona_5_RPG_Podrecznik_Gracza.docx'));
  assert.equal(await page.evaluate(async()=>{try{await window.desktop.openManual('../../plik');return false;}catch{return true;}}),true);
  await screenshot(page,'podreczniki-word.png');await page.getByRole('button',{name:'Zamknij podręczniki',exact:true}).click();
  if(packaged){const resources=await app.evaluate(()=>process.resourcesPath);for(const name of ['Persona_5_RPG_Podrecznik_Gracza.docx','Persona_5_RPG_Podrecznik_GM.docx','Persona_5_RPG_Bestiariusz.docx'])assert.ok((await fs.stat(path.join(resources,'podreczniki',name))).size>10000);}
  await page.getByRole('button',{name:'05 Karty i PDF',exact:true}).click();
  const printed=await page.locator('#print-root').innerText();assert.ok(printed.includes('Lek ×2'));assert.ok(printed.includes('Latarka i stary plecak'));assert.equal(printed.includes('PRYWATNY_TROP_SESJI'),false);
  const jsonFile=path.join(output,'sesja-postac.json');await app.evaluate(({dialog},file)=>{dialog.showSaveDialog=async()=>({canceled:false,filePath:file});},jsonFile);await page.getByRole('button',{name:'Zapisz do pliku'}).click();await page.getByText('Zapisano plik postaci.',{exact:true}).waitFor();
  const exported=JSON.parse(await fs.readFile(jsonFile,'utf8'));assert.equal(exported.exp,5500);assert.equal(exported.hp,8);assert.equal(exported.sp,2);assert.equal(exported.spent,5);assert.equal(exported.skills.length,8);assert.equal(exported.items[0].quantity,2);assert.equal(exported.social.Wiedza,2);
  const pdfFile=path.join(output,'sesja-karty.pdf');await app.evaluate(({dialog},file)=>{dialog.showSaveDialog=async()=>({canceled:false,filePath:file});},pdfFile);await page.getByRole('button',{name:'Zapisz PDF ↗',exact:true}).click();await page.getByText('Zapisano karty w PDF.',{exact:true}).waitFor();assert.ok((await fs.stat(pdfFile)).size>10000);
  await page.getByRole('status').filter({hasText:'Zapisano automatycznie'}).waitFor();
  await app.close();app=await launch();page=await app.firstWindow();page.setDefaultTimeout(15000);await page.getByRole('navigation',{name:'Prowadzenie postaci'}).waitFor();
  assert.equal(await page.getByLabel('Aktualne HP').inputValue(),'8');assert.equal(await page.getByLabel('Aktualne SP').inputValue(),'2');
  const original=await page.getByLabel('Lokalne postacie').inputValue();
  await page.getByRole('button',{name:/Nowa postać/}).click();await page.getByRole('navigation',{name:'Kroki kreatora'}).waitFor();
  await page.getByLabel('Lokalne postacie').selectOption(original);await page.getByRole('navigation',{name:'Prowadzenie postaci'}).waitFor();
  await page.getByRole('button',{name:'03 Ekwipunek',exact:true}).click();assert.equal(await page.getByLabel('Ilość: Lek',{exact:true}).inputValue(),'2');
  await page.getByRole('button',{name:'04 Notatki i cechy',exact:true}).click();assert.equal(await page.getByLabel('Notatki i uzgodnienia z GM').inputValue(),'PRYWATNY_TROP_SESJI');
  assert.deepEqual(errors,[]);
  await fs.writeFile(path.join(output,packaged?'sesja-spakowana.json':'sesja-wynik.json'),JSON.stringify({wynik:'OK',spakowana:packaged,kontrole:['domyślny pulpit aktywnej postaci','HP/SP i dolne granice','EXP i awans bez leczenia','nauka z zastąpieniem jednego z ośmiu skilli','ekwipunek z ilościami i zachowanie starego opisu','prywatne notatki i rangi','aktualne podręczniki: odczyt i kopia Word','eksport JSON i PDF','ponowne uruchomienie i przełączanie trybu po wyborze postaci']},null,2));
  console.log('OK: pulpit, awans, nauka, ekwipunek, notatki, podręczniki Word i zapis sesji.');
 }finally{if(app)await app.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

