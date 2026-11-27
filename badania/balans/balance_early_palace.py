# UWAGA: badanie archiwalne z 2026-10-29. Dotyczy starej wersji podręczników
# (GM 0.7, Gracza 0.4, Bestiariusz 0.4) i danych skill_*_0_7.json, więc wyniki
# i reguły w tym skrypcie mogą nie odpowiadać aktualnym podręcznikom.
# Wymagane pliki wejściowe są w historii Git pod tagiem archiwum-przed-porzadkami
# (np. git restore --source archiwum-przed-porzadkami -- Persona_5_RPG_Podrecznik_GM_0_7.docx)
# i trzeba je umieścić obok skryptu, razem z p5_base_skill_data.json i p5r_skill_data.json
# z dane/kompendium/. Wyniki to materiał badawczy, nie obowiązujące zasady.
import balance_lab as B
import time

def run(n=400):
    cells=[];fights=0
    for level,size in [(1,2),(5,2),(5,4)]:
        ps=B.pool(level)
        for count_delta in [0,1]:
            for wake in [False,True]:
                for rest in [False,True]:
                    results=[]
                    for i in range(n):
                        heroes=B.party(level,size,'balanced',B.FINAL,social=True);kit={'hp':4,'sp':1,'revive':0};acc=B.Counter();ok=True;total=0;cleared=0
                        for step in range(7):
                            if rest and step==3:
                                for u in heroes:u.hp=u.maxhp;u.sp=u.maxsp
                                kit['hp']=min(9,kit['hp']+4);kit['sp']=min(10-kit['hp'],kit['sp']+1)
                            p=ps[(i+step*3)%len(ps)];enemies=[B.make_enemy(p,k) for k in range(size+count_delta)] if step<6 else [B.make_enemy(p,0,True,size,2 if size==4 else 1,0)]
                            f=B.Fight(heroes,enemies,7919*i+level*100000+step*101+size,B.FINAL,False,'heroes' if step in (0,3) else 'none',kit=kit)
                            res=f.run();fights+=1;total+=res['rounds'];acc.update(res['metrics'])
                            if res['outcome'] not in ('victory','negotiated'):ok=False;break
                            cleared+=1
                            if wake:
                                for u in heroes:
                                    if not u.alive:u.hp=1;acc['post_battle_wakeups']+=1
                            for healer in heroes:
                                for target in heroes:
                                    if not target.alive:continue
                                    for _ in range(20):
                                        av=[s for s in healer.skills if s.kind=='heal' and not s.area and f.available(healer,s)]
                                        if target.hp>=target.maxhp*.85 or not av:break
                                        def efficiency(s):return min(target.maxhp-target.hp,target.maxhp if s.amount<0 else s.amount)/max(1,B.cost_of(s,healer,B.FINAL))
                                        s=max(av,key=efficiency);c=B.cost_of(s,healer,B.FINAL)
                                        if target.maxhp-target.hp<(target.maxhp if s.amount<0 else s.amount)*.4:break
                                        healer.sp-=c;acc['out_of_combat_SP_paid']+=c;target.hp=min(target.maxhp,target.hp+(target.maxhp if s.amount<0 else s.amount))
                        results.append({'outcome':'victory' if ok else 'defeat','rounds':total,'hp_pct':100*sum(u.hp for u in heroes)/sum(u.maxhp for u in heroes),'sp_pct':100*sum(u.sp for u in heroes)/sum(u.maxsp for u in heroes),'metrics':dict(acc),'cleared':cleared})
                    cells.append({'level':level,'party_size':size,'ordinary_enemy_count':size+count_delta,'wake_to_1_HP_after_victory':wake,'full_return_after_third_fight':rest,'rules':'revised_costs_plus_optional_wakeup','build':'balanced',**B.summarize(results),'mean_encounters_cleared':round(B.statistics.mean(r['cleared'] for r in results),3)})
        B.dump('early_palace_partial.json',cells);print('EARLY PALACE',level,size,flush=True)
    B.dump('early_palace_calibration.json',cells);B.dump('early_palace_run.json',{'attempts':len(cells)*n,'actual_fights':fights,'cells':len(cells)});print('EARLY TESTS DONE',flush=True)
if __name__=='__main__':run()
