const { build } = require('./package.json');

const [owner, repo] = (process.env.GITHUB_REPOSITORY ?? '').split('/');
if (!owner || !repo) throw new Error('Ustaw GITHUB_REPOSITORY na właściciel/repozytorium.');

module.exports = {
  ...build,
  publish: { provider: 'github', owner, repo },
  artifactName: 'Take-Your-Heart-${version}-${os}-${arch}.${ext}',
  win: { ...build.win, target: 'nsis' },
  mac: process.env.CSC_LINK
    ? { ...build.mac, target: ['dmg', 'zip'] }
    : { ...build.mac, target: 'dmg', identity: null, publish: null },
  linux: { ...build.linux, target: 'AppImage' },
};
