// Przenośna paczka Linux x64; działa także podczas budowania na Windowsie.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const {createRequire} = require('node:module');
// Korzystamy z tej samej biblioteki tar co przypięty w lockfile electron-builder.
const tar = createRequire(require.resolve('app-builder-lib'))('tar');
const root = path.resolve(__dirname, '..');
const source = path.join(root, 'release/linux-unpacked');
const {version} = require('../package.json');
const folder = `Take-Your-Heart-${version}-linux-x64`;
const output = path.join(root, 'release', folder + '.tar.gz');
const executables = new Set(['take-your-heart', 'chrome-sandbox', 'chrome_crashpad_handler', 'Uruchom.sh']);

(async () => {
  const binary = await fs.readFile(path.join(source, 'take-your-heart'));
  if (binary.subarray(0, 4).toString('hex') !== '7f454c46' || binary[4] !== 2 || binary.readUInt16LE(18) !== 62) {
    throw new Error('Oczekiwano programu ELF dla Linuxa x86-64.');
  }
  await fs.copyFile(path.join(root, 'LINUX.txt'), path.join(source, 'LINUX.txt'));
  await fs.writeFile(path.join(source, 'Uruchom.sh'), '#!/bin/sh\nset -eu\ncd -- "$(dirname -- "$0")"\nexec ./take-your-heart "$@"\n');
  await tar.create({
    file: output, cwd: source, prefix: folder, gzip: true, portable: true,
    // NTFS nie przechowuje praw wykonywania Linuksa; ustawiamy je w archiwum.
    onWriteEntry(entry) {
      entry.stat.mode = entry.type === 'Directory' || executables.has(path.basename(entry.path)) ? 0o755 : 0o644;
    },
  }, ['.']);
  const entries = new Map();
  await tar.list({file: output, onReadEntry: entry => entries.set(entry.path.replace('/./', '/'), entry.mode & 0o777)});
  for (const name of executables) {
    if (entries.get(`${folder}/${name}`) !== 0o755) throw new Error(`Brak prawa uruchamiania: ${name}`);
  }
  for (const name of ['resources/app.asar', 'LINUX.txt', ...['Gracza', 'GM', 'Bestiariusz'].map(kind =>
    'resources/podreczniki/' + (kind === 'Bestiariusz' ? 'Persona_5_RPG_Bestiariusz.docx' : `Persona_5_RPG_Podrecznik_${kind}.docx`))]) {
    if (!entries.has(`${folder}/${name}`)) throw new Error(`Brak pliku w paczce: ${name}`);
  }
  const hash = crypto.createHash('sha256').update(await fs.readFile(output)).digest('hex');
  await fs.writeFile(output + '.sha256', `${hash}  ${path.basename(output)}\n`);
  console.log(`Gotowe: ${output}\nSprawdzono ELF x64, zawartość i prawa wykonywania. SHA256: ${hash}`);
})().catch(error => {console.error(error); process.exitCode = 1;});
