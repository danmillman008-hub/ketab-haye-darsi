const assert=require('node:assert/strict'),fs=require('fs'),p=JSON.parse(fs.readFileSync('plan.json'));
assert.equal(p.length,12);
for(let w=1;w<=2;w++){
 const ds=p.filter(x=>x.week===w),bs=ds.flatMap(x=>x.boxes);
 assert.equal(ds.reduce((a,x)=>a+x.hours,0),47);assert.equal(ds.reduce((a,x)=>a+x.tests,0),495);
 for(const [name,count,tests] of [['زیست',9,120],['ریاضی',6,150],['فیزیک',6,150],['شیمی',6,75]]){
 const b=bs.filter(x=>x.subject.startsWith(name));assert.equal(b.length,count);assert.equal(b.reduce((a,x)=>a+x.tests,0),tests);
 }
 for(const d of ds)assert.equal(new Set(d.boxes.map(x=>x.subject)).size,2);
}
assert.equal((fs.readFileSync('index.html','utf8').match(/class="[^\"]* sheet"/g)||[]).length,4);
console.log('PASS: 12 study days, two subjects/day, 4 sheets, all box/test/hour totals');

for(const d of p){
 const order=d.boxes.map(b=>b.subject.split(' ')[0]);
 assert.deepEqual(order,d.day%2===0?['زیست','ریاضی','زیست','ریاضی','زیست']:['فیزیک','شیمی','فیزیک','شیمی']);
 for(const subject of new Set(d.boxes.map(x=>x.subject))){
  const bs=d.boxes.filter(b=>b.subject===subject);
  const lesson=bs.findIndex(b=>b.tests===0);
  if(lesson>=0) assert.equal(lesson,0);
 }
}
const html=fs.readFileSync('index.html','utf8');
assert(!html.includes('بدون باکس درسی اضافه'));
console.log('PASS: alternating subjects and lesson-before-test order');

assert.equal(p.reduce((n,d)=>n+d.hours,0),94);
assert.deepEqual(p.map(d=>d.hours),[8,7,9,7,9,7,8,7,9,7,9,7]);
for(const d of p){
 assert.equal(d.hours,d.boxes.reduce((n,b)=>n+b.hours,0));
 for(const b of d.boxes.filter(b=>b.subject.startsWith('زیست'))){
  assert.equal(b.hours,b.tests>0?2:1);
  assert.equal(b.tests,b.tests>0?20:0);
 }
}
console.log('PASS: biology reading remains 1h, each 20-test box is 2h; weekly 47h, total 94h');
