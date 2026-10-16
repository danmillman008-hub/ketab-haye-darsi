const assert=require('node:assert/strict'),fs=require('fs'),p=JSON.parse(fs.readFileSync('plan.json'));
assert.equal(p.length,12);
for(let w=1;w<=2;w++){
 const ds=p.filter(x=>x.week===w),bs=ds.flatMap(x=>x.boxes);
 assert.equal(ds.reduce((a,x)=>a+x.hours,0),41);assert.equal(ds.reduce((a,x)=>a+x.tests,0),495);
 for(const [name,count,tests] of [['زیست',9,120],['ریاضی',6,150],['فیزیک',6,150],['شیمی',6,75]]){
 const b=bs.filter(x=>x.subject.startsWith(name));assert.equal(b.length,count);assert.equal(b.reduce((a,x)=>a+x.tests,0),tests);
 }
 for(const d of ds)assert.equal(new Set(d.boxes.map(x=>x.subject)).size,2);
}
assert.equal((fs.readFileSync('index.html','utf8').match(/class="[^\"]* sheet"/g)||[]).length,4);
console.log('PASS: 12 study days, two subjects/day, 4 sheets, all box/test/hour totals');
