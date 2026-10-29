// Wektorowa gwiazda kreatora; PNG i wielorozmiarowe ICO bez dodatkowych bibliotek.
const fs=require('node:fs');
const path=require('node:path');
const zlib=require('node:zlib');
const points=Array.from({length:10},(_,i)=>{const a=-Math.PI/2-Math.PI/12+i*Math.PI/5,r=i%2?12:29;return[32+Math.cos(a)*r,32+Math.sin(a)*r];});
const directory=__dirname;
const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><polygon fill="#ed1838" points="${points.map(p=>p.map(x=>x.toFixed(3)).join(',')).join(' ')}"/></svg>\n`;
fs.mkdirSync(path.join(directory,'../src/assets'),{recursive:true});
fs.writeFileSync(path.join(directory,'../src/assets/star.svg'),svg);
const crcTable=Array.from({length:256},(_,n)=>{let c=n;for(let i=0;i<8;i++)c=c&1?0xedb88320^(c>>>1):c>>>1;return c>>>0;});
function crc(buffer){let c=0xffffffff;for(const byte of buffer)c=crcTable[(c^byte)&255]^(c>>>8);return(c^0xffffffff)>>>0;}
function chunk(name,bytes){const type=Buffer.from(name),length=Buffer.alloc(4),check=Buffer.alloc(4);length.writeUInt32BE(bytes.length);check.writeUInt32BE(crc(Buffer.concat([type,bytes])));return Buffer.concat([length,type,bytes,check]);}
function inside(x,y){let result=false;for(let i=0,j=points.length-1;i<points.length;j=i++){const a=points[i],b=points[j];if((a[1]>y)!==(b[1]>y)&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])result=!result;}return result;}
function png(size){const bytes=Buffer.alloc(size*(size*4+1));for(let y=0;y<size;y++)for(let x=0;x<size;x++){let coverage=0;for(let sy=0;sy<4;sy++)for(let sx=0;sx<4;sx++)if(inside((x+(sx+.5)/4)*64/size,(y+(sy+.5)/4)*64/size))coverage++;const offset=y*(size*4+1)+1+x*4;bytes[offset]=coverage?237:0;bytes[offset+1]=coverage?24:0;bytes[offset+2]=coverage?56:0;bytes[offset+3]=Math.round(coverage*255/16);}const header=Buffer.alloc(13);header.writeUInt32BE(size,0);header.writeUInt32BE(size,4);header[8]=8;header[9]=6;return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',header),chunk('IDAT',zlib.deflateSync(bytes)),chunk('IEND',Buffer.alloc(0))]);}
const sizes=[16,24,32,48,64,128,256],images=sizes.map(png),header=Buffer.alloc(6+16*sizes.length);header.writeUInt16LE(1,2);header.writeUInt16LE(sizes.length,4);let offset=header.length;
images.forEach((bytes,i)=>{const p=6+16*i;header[p]=sizes[i]===256?0:sizes[i];header[p+1]=header[p];header.writeUInt16LE(1,p+4);header.writeUInt16LE(32,p+6);header.writeUInt32LE(bytes.length,p+8);header.writeUInt32LE(offset,p+12);offset+=bytes.length;});
fs.writeFileSync(path.join(directory,'icon.ico'),Buffer.concat([header,...images]));
fs.writeFileSync(path.join(directory,'icon.png'),images.at(-1));
console.log('Utworzono gwiazdę SVG, PNG i ICO (16–256 px).');
