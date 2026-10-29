"""Sensitivity to safer healing, efficient legal area heals and early encounter density."""
import balance_lab as B

def recover(heroes,fix,acc):
    # Outside combat there is no action pressure: choose the best legal useful HP/SP ratio.
    for _ in range(100):
        alive=[u for u in heroes if u.alive]
        if not alive or all(u.hp>=u.maxhp*.85 for u in alive):return
        options=[]
        for caster in alive:
            for s in caster.skills:
                if s.kind!='heal':continue
                c=B.cost_of(s,caster,fix)
                if caster.sp<c:continue
                for target in (alive[:1] if s.area else alive):
                    targets=alive if s.area else [target]
                    useful=sum(min(u.maxhp-u.hp,u.maxhp if s.amount<0 else s.amount) for u in targets)
                    theoretical=sum(u.maxhp if s.amount<0 else s.amount for u in targets)
                    if useful and useful>=.4*theoretical:options.append((useful/max(1,c),useful,-c,caster,s,targets))
        if not options:return
        _,_,_,caster,s,targets=max(options,key=lambda x:x[:3]);c=B.cost_of(s,caster,fix);caster.sp-=c;acc['out_of_combat_SP_paid']+=c
        for u in targets:u.hp=min(u.maxhp,u.hp+(u.maxhp if s.amount<0 else s.amount))

def one_route(level,size,enemy_count,wake,rest,fix,seed):
    heroes=B.party(level,size,'balanced',fix,advanced=level>=25,social=True);kit={'hp':4,'sp':1,'revive':0};acc=B.Counter();cleared=0;total=0;ok=True;ps=B.pool(level)
    for step in range(7):
        if rest and step==3:
            for u in heroes:u.hp=u.maxhp;u.sp=u.maxsp
            kit['hp']=min(9,kit['hp']+4);kit['sp']=min(10-kit['hp'],kit['sp']+1)
        p=ps[(seed+step*3)%len(ps)];enemies=[B.make_enemy(p,k) for k in range(enemy_count)] if step<6 else [B.make_enemy(p,0,True,size,2 if size==4 else 1,0)]
        f=B.Fight(heroes,enemies,7919*seed+level*100000+step*101+size,fix,False,'heroes' if step in (0,3) else 'none',kit=kit);f.heal_threshold=.65
        res=f.run();total+=res['rounds'];acc.update(res['metrics'])
        if res['outcome'] not in ('victory','negotiated'):ok=False;break
        cleared+=1
        if wake:
            for u in heroes:
                if not u.alive:u.hp=1;acc['wakeups']+=1
        recover(heroes,fix,acc)
    return {'outcome':'victory' if ok else 'defeat','rounds':total,'hp_pct':100*sum(u.hp for u in heroes)/sum(u.maxhp for u in heroes),'sp_pct':100*sum(u.sp for u in heroes)/sum(u.maxsp for u in heroes),'metrics':dict(acc),'cleared':cleared,'actual_fights':cleared+(0 if ok else 1)}

def run(n=350):
    cells=[];fights=0;attempts=0
    fixtures=[(1,2,1),(1,2,2),(5,2,1),(5,2,2),(5,2,3),(25,2,3),(25,4,5),(65,2,3),(65,4,5)]
    for level,size,count in fixtures:
        for wake in [False,True]:
            for rest in [False,True]:
                for fix in [B.BASE,B.FINAL]:
                    # Below L50 a balanced duet has no paid Physical/Gun nor severe spells.
                    if level<50 and size==2 and fix is B.FINAL:continue
                    results=[one_route(level,size,count,wake,rest,fix,i) for i in range(n)];attempts+=n;fights+=sum(r['actual_fights'] for r in results)
                    cells.append({'level':level,'party_size':size,'ordinary_enemy_count':count,'wake_after_victory':wake,'return_after_third_fight':rest,'heal_threshold':.65,'efficient_area_healing_outside_combat':True,'rules':fix.label,**B.summarize(results),'mean_encounters_cleared':round(B.statistics.mean(r['cleared'] for r in results),3)})
        B.dump('sensitivity_partial.json',cells);print('SENSITIVITY',level,size,count,flush=True)
    B.dump('healing_and_encounter_sensitivity.json',cells);B.dump('sensitivity_run.json',{'attempts':attempts,'actual_fights':fights,'cells':len(cells)});print('SENSITIVITY DONE',flush=True)
if __name__=='__main__':run()
