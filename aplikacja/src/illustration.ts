import {MAX_STORED_IMAGE_BYTES} from './model';

export const MAX_UPLOAD_MB = 100;
export const MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1_000_000;
const MAX_EDGE = 2048;

export async function prepareIllustration(file:File):Promise<Blob>{
 if(file.size<=MAX_STORED_IMAGE_BYTES)return file;
 const image=await createImageBitmap(file);
 const canvas=document.createElement('canvas');
 try{
  const scale=Math.min(1,MAX_EDGE/Math.max(image.width,image.height));
  canvas.width=Math.max(1,Math.round(image.width*scale));
  canvas.height=Math.max(1,Math.round(image.height*scale));
  const context=canvas.getContext('2d');
  if(!context)throw new Error('Brak kontekstu obrazu.');
  context.drawImage(image,0,0,canvas.width,canvas.height);
  return await new Promise<Blob>((resolve,reject)=>{
   canvas.toBlob(blob=>{
    if(blob?.type==='image/webp'&&blob.size<=MAX_STORED_IMAGE_BYTES)resolve(blob);
    else reject(new Error('Nie udało się zmniejszyć ilustracji.'));
   },'image/webp',0.9);
  });
 }finally{
  image.close();
  canvas.width=canvas.height=0;
 }
}
