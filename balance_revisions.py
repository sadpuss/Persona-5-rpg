import balance_lab as B
import balance_focus as F
import time,json

def regression(n=350):
    out=[]
    # Re-test every physical matrix cell where the first proposal lost at least 3pp.
    wide=json.loads((B.OUT/'encounter_matrix.json').read_text(encoding='utf-8'))
    d={(r['level'],r['party_size'],r['known_weaknesses'],r['surprise'],r['build'],r['rules']):r for r in wide}
    targets=[]
    for key,a in d.items():
        if key[-1]=='baseline' and key[4]=='physical':
            b=d[key[:-1]+('proposed',)]
            if b['win_pct']-a['win_pct']<=-3:targets.append(key[:-1])
    targets+= [(lv,size,known,surprise,'physical') for lv in [1,5,10,25,35,50,65,99] for size in [1,2,4] for known in [False,True] for surprise in ['none']]
    targets=list(dict.fromkeys(targets))
    for level,size,known,surprise,build in targets:
        ps=B.pool(level)
        for fix in [B.BASE,B.PATCH,B.FINAL]:
            results=[]
            for i in range(n):
                heroes=B.party(level,size,build,fix,advanced=level>=25);p=ps[i%len(ps)];enemies=[B.make_enemy(p,k) for k in range(size+1)]
                f=B.Fight(heroes,enemies,1000003*level+97*i+size,fix,known,surprise)
                results.append(f.run())
            out.append({'level':level,'party_size':size,'known':known,'surprise':surprise,'build':build,'rules':fix.label,**B.summarize(results)})
    B.dump('physical_revision_regression.json',out);return len(out)*n

def start_encounters(n=1000):
    out=[]
    for size in [1,2,4]:
        for foes in sorted({max(1,size-1),size,size+1}):
            for surprise in ['heroes','none','enemies']:
                for fix in [B.BASE,B.FINAL]:
                    results=[]
                    ps=B.pool(1)
                    for i in range(n):
                        heroes=B.party(1,size,'balanced',fix);p=ps[i%len(ps)];enemies=[B.make_enemy(p,k) for k in range(foes)]
                        f=B.Fight(heroes,enemies,2718281+i*53+size,fix,False,surprise)
                        results.append(f.run())
                    out.append({'level':1,'party_size':size,'enemy_count':foes,'surprise':surprise,'rules':fix.label,**B.summarize(results)})
    B.dump('level1_encounter_calibration.json',out);return sum(r['n'] for r in out)

def final_physical_palaces(n=250):
    out=[];fights=0
    for level in [5,25,65]:
        for size in [1,2,4]:
            for build in ['physical']+(['balanced'] if size==4 else []):
                for rest in [False,True]:
                    results=[]
                    fix=B.FINAL;ps=B.pool(level)
                    for i in range(n):
                        heroes=B.party(level,size,build,fix,advanced=level>=25,social=True);kit={'hp':4,'sp':1,'revive':0};acc=B.Counter();ok=True;total=0;cleared=0
                        for step in range(7):
                            if rest and step==3:
                                for u in heroes:u.hp=u.maxhp;u.sp=u.maxsp
                                kit['hp']=min(9,kit['hp']+4);kit['sp']=min(10-kit['hp'],kit['sp']+1)
                            p=ps[(i+step*3)%len(ps)];enemies=[B.make_enemy(p,k) for k in range(size+1)] if step<6 else [B.make_enemy(p,0,True,size,2 if size==4 else 1,0)]
                            f=B.Fight(heroes,enemies,7919*i+level*100000+step*101+size,fix,False,'heroes' if step in (0,3) else 'none',kit=kit)
                            res=f.run();fights+=1;total+=res['rounds'];acc.update(res['metrics'])
                            if res['outcome'] not in ('victory','negotiated'):ok=False;break
                            cleared+=1
                            for healer in heroes:
                                for target in heroes:
                                    if not target.alive:continue
                                    for _ in range(20):
                                        av=[s for s in healer.skills if s.kind=='heal' and not s.area and f.available(healer,s)]
                                        if target.hp>=target.maxhp*.85 or not av:break
                                        def efficiency(s):return min(target.maxhp-target.hp,target.maxhp if s.amount<0 else s.amount)/max(1,B.cost_of(s,healer,fix))
                                        s=max(av,key=efficiency);c=B.cost_of(s,healer,fix)
                                        if target.maxhp-target.hp<(target.maxhp if s.amount<0 else s.amount)*.4:break
                                        healer.sp-=c;acc['out_of_combat_SP_paid']+=c;target.hp=min(target.maxhp,target.hp+(target.maxhp if s.amount<0 else s.amount))
                        results.append({'outcome':'victory' if ok else 'defeat','rounds':total,'hp_pct':100*sum(u.hp for u in heroes)/sum(u.maxhp for u in heroes),'sp_pct':100*sum(u.sp for u in heroes)/sum(u.maxsp for u in heroes),'metrics':dict(acc),'cleared':cleared})
                    out.append({'level':level,'party_size':size,'build':build,'full_return_after_third_fight':rest,'rules':fix.label,**B.summarize(results),'mean_encounters_cleared':round(B.statistics.mean(r['cleared'] for r in results),3)})
        B.dump('final_palace_partial.json',out);print('FINAL PALACE LEVEL',level,flush=True)
    B.dump('final_physical_palaces.json',out);return sum(r['n'] for r in out),fights

def guard_test(n=10000):
    out=[]
    for guard in [False,True]:
        both_alive=0;damage=[]
        for seed in range(n):
            rng=B.random.Random(seed+445566);raw=sum(rng.randint(1,6) for _ in range(3))+8;hp=[20,20]
            for i,mult in enumerate([1.5,1]):
                if rng.randint(1,20)+4>=12:hp[i]-=int(raw*mult*(.4 if guard else 1))
            both_alive+=all(h>0 for h in hp);damage.append(sum(20-max(0,h) for h in hp))
        out.append({'guard':guard,'n':n,'both_survive_pct':100*both_alive/n,'mean_team_damage':B.statistics.mean(damage),'fixture':'One telegraphed heavy Fire AoE against two L25 heroes currently at 20 HP; one Weak Fire, one Normal; same damage roll and attack rolls.'})
    B.dump('guard_telegraph_test.json',out)

if __name__=='__main__':
    start=time.time();guard_test();B.dump('final_dominance.json',F.exact_dominance(B.FINAL));print('FINAL CATALOGUE CHECK COMPLETE',flush=True)
    a=regression();print('PHYSICAL REGRESSIONS COMPLETE',a,flush=True)
    b=start_encounters();print('START CALIBRATION COMPLETE',b,flush=True)
    c,d=final_physical_palaces();B.dump('revision_run.json',{'physical_regression_fights':a,'start_calibration_fights':b,'final_palace_attempts':c,'final_palace_actual_fights':d,'guard_trials':20000,'seconds':round(time.time()-start,2)});print('DONE',round(time.time()-start,2),flush=True)
