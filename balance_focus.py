"""Independent focused checks and counterexample traces; no rulebook edits."""
import balance_lab as B
import random,math,statistics,json
from collections import Counter

def pure_damage_u(u,s,fix):return s.flat+(2 if fix.light_damage and s.elem in ('Physical','Gun') and s.name not in ('Basic Physical','Basic Gun') and (s.dice,s.flat)==B.TIERS['light'] else 0)

def exact_dominance(fix):
    u=B.make_hero(99,0,'mage',fix);out=[];conditional={'Cornered Fang','Deadly Fury','Giant Slice','Rising Slash'}
    skills=sorted([s for s in B.SKILLS.values() if s.kind=='attack'],key=lambda s:B.cost_of(s,u,fix))
    for bad in skills:
        if bad.name.startswith('Basic ') or bad.name in conditional:continue
        for good in skills:
            if good.name==bad.name or good.name in conditional or good.elem!=bad.elem or good.area!=bad.area or good.resource!=bad.resource:continue
            if (good.status,good.dc)!=(bad.status,bad.dc):continue
            if B.gates.get(good.name,{'min_level':1})['min_level']>B.gates[bad.name]['min_level']:continue
            if good.dice==bad.dice and pure_damage_u(u,good,fix)>=pure_damage_u(u,bad,fix) and good.accuracy>=bad.accuracy and B.cost_of(good,u,fix)<B.cost_of(bad,u,fix):
                out.append({'bad':bad.name,'better':good.name,'bad_cost':B.cost_of(bad,u,fix),'better_cost':B.cost_of(good,u,fix)});break
    return out

def farm(n=5000):
    rows=[]
    for mode in ['Invigorate','Spirit Drain']:
        for patch in [False,True]:
            for cycles in [1,5,10]:
                endsp=[];endhp=[];faints=0;totalcasts=0
                for seed in range(n):
                    rng=random.Random(8017+seed);maxhp=99;maxsp=95;hp=maxhp;sp=0;group_turns=0;enemy_sp=12
                    for cycle in range(cycles):
                        # At the start of a re-engagement old rules replenish enemy SP.
                        if not patch:enemy_sp=12
                        for turn in range(1,4):
                            if mode=='Spirit Drain':
                                # Supply first cast externally only in this focused fixture.
                                if cycle==0 and turn==1:sp=1
                                if sp:
                                    sp-=1;totalcasts+=1
                                    if rng.randint(1,20)+5>=12:
                                        stolen=min(3,enemy_sp);enemy_sp-=stolen;sp=min(maxsp,sp+stolen)
                            # The initial three ordinary turns use Guard for Invigorate, otherwise a drain.
                            if rng.randint(1,20)+4>=12:
                                if enemy_sp>=2:enemy_sp-=2;damage=sum(rng.randint(1,6) for _ in range(2))+6;damage*=.5 # Resist Wind
                                else:damage=rng.randint(1,6)+4
                                hp-=math.floor(damage*(.4 if mode=='Invigorate' else 1))
                            group_turns+=1
                            if mode=='Invigorate' and (not patch or group_turns<=3):sp=min(maxsp,sp+3)
                            if hp<=0:break
                        if hp<=0:break
                        # Flee uses the ordinary action, so Guard has expired on this turn.
                        for _ in range(30):
                            if rng.randint(1,20)>=11:break
                            if rng.randint(1,20)+4>=12:
                                if enemy_sp>=2:enemy_sp-=2;damage=(sum(rng.randint(1,6) for _ in range(2))+6)*.5
                                else:damage=rng.randint(1,6)+4
                                hp-=math.floor(damage)
                            if hp<=0:break
                        if hp<=0:break
                        # Legal outside-combat Diarama + Spell Master: 20 HP for 1 SP.
                        while hp<=maxhp-15 and sp>0:sp-=1;hp=min(maxhp,hp+20)
                    if hp<=0:faints+=1
                    endsp.append(max(0,sp));endhp.append(max(0,hp))
                rows.append({'mode':mode,'patched_encounter_persistence':patch,'cycles':cycles,'n':n,'median_SP':statistics.median(endsp),'mean_SP':round(statistics.mean(endsp),3),'median_HP':statistics.median(endhp),'KO_pct':round(faints/n*100,2),'grant_EXP':0,'special_fixture':'Hero L65, Resist Wind, Invigorate 3 or Spirit Drain, Spell Master/Diarama; one ordinary medium-Wind shadow with 12 SP; its HP resets on re-entry; no incoming status; escape d20 DC11.'})
    B.dump('retreat_resource_farming.json',rows);return rows

def despair_combat(n=1800):
    rows=[]
    for hp in [140,300,600]:
        for fix in [B.BASE,B.PATCH]:
            results=[]
            for seed in range(n):
                heroes=B.party(10,2,'balanced',fix);heroes[0].skills.append(B.SKILLS['Ominous Words'])
                # Replace one starting skill so the build stays within eight and the level budget.
                heroes[0].skills.pop(1)
                p=B.pool(10)[0];enemy=B.make_enemy(p,0,True,2);enemy.hp=enemy.maxhp=hp;enemy.aff={}
                f=B.Fight(heroes,[enemy],seed+800000,fix,True,'heroes',limit=6)
                original=f.choice;attempted=[False]
                def choose(u):
                    if u.side:
                        return original(u)
                    if u.uid==heroes[0].uid and not attempted[0]:attempted[0]=True;return ('skill',B.SKILLS['Ominous Words'],enemy)
                    return ('guard',None,u)
                f.choice=choose
                result=f.run();result['boss_hp_left']=enemy.hp;results.append(result)
            rows.append({'boss_start_hp':hp,'rules':fix.label,**B.summarize(results),'mean_boss_hp_lost':round(statistics.mean(hp-r['boss_hp_left'] for r in results),2),'test':'Exactly one legal Ominous Words attempt; then Guard only; one normal boss action/turn; six-turn window; no direct hero damage.'})
    B.dump('despair_full_combat.json',rows);return rows

def price_duels(n=1500):
    rows=[]
    for level in [50,65,99]:
        for advanced in [False,True]:
            for policy in ['efficient','burst']:
                for fix in [B.BASE,B.MAGICPAIR]:
                    results=[]
                    for seed in range(n):
                        heroes=B.party(level,2,'burst',fix,advanced=advanced)
                        # Keep a heavy skill as an available deliberate fallback, at the price of a slot.
                        for i,u in enumerate(heroes):
                            u.skills[0]=B.SKILLS['Agidyne' if i==0 else 'Garudyne']
                        p=B.pool(level)[0];enemy=B.make_enemy(p,0,True,2);enemy.aff={'Physical':'Null','Gun':'Null','Wind':'Resist'}
                        f=B.Fight(heroes,[enemy],seed+540000,fix,True,'none',policy,limit=30)
                        results.append(f.run())
                    rows.append({'level':level,'advanced_passives':advanced,'policy':policy,'rules':fix.label,**B.summarize(results),'fixture':'Two mages, neutral Fire/resisted Wind, Null Physical/Gun, same one-action miniboss and HP before/after; one heavy fallback in addition to severe attacks.'})
    B.dump('isolated_magic_prices.json',rows);return rows

def reference_traces():
    output=[]
    for level in [5,25,65]:
        for fix in [B.BASE,B.PATCH]:
            heroes=B.party(level,2,'balanced',fix,advanced=level>=25,social=True);kit={'hp':4,'sp':1,'revive':0};encounters=[]
            for step in range(7):
                p=B.pool(level)[step%len(B.pool(level))]
                enemies=[B.make_enemy(p,i) for i in range(3)] if step<6 else [B.make_enemy(p,0,True,2)]
                fight=B.Fight(heroes,enemies,20261029+level+step,fix,False,'heroes' if step in (0,3) else 'none',kit=kit)
                fight.trace=[];result=fight.run()
                encounters.append({'step':step+1,'enemy':p,'hero_skills':[[s.name for s in u.skills]+sorted(u.passives) for u in heroes],'result':result,'trace':fight.trace,'resources_after':[[u.hp,u.sp] for u in heroes],'stock':dict(kit)})
                if result['outcome'] not in ('victory','negotiated'):break
            output.append({'level':level,'rules':fix.label,'note':'Action trace sample; deliberately no inter-fight healing in this reference trace, unlike the main palace matrix.','encounters':encounters})
    B.dump('reference_action_traces.json',output)

def deterministic_families():
    findings={}
    for fix in [B.BASE,B.PATCH]:findings[fix.label+'_strict_dominated_skills']=exact_dominance(fix)
    # No false dominance claims for conditional Surrounded/Baton Pass attacks.
    findings['ignored_conditional_effects']=['Cornered Fang','Deadly Fury','Giant Slice','Rising Slash']
    # Costs: arbitrary source percentages should not reappear every time a fixed-HP skill is used.
    hero=B.make_hero(99,0,'mage',B.BASE)
    findings['examples']=[]
    for name in ['Basic Physical','Cleave','Stomach Blow',"God's Hand",'Brave Blade','Sword Dance','Agidyne','Inferno','Maragidyne','Blazing Hell']:
        s=B.SKILLS[name];findings['examples'].append({'name':name,'mean_before':s.mean,'mean_after':s.dice*3.5+pure_damage_u(hero,s,B.PATCH),'cost_before':B.cost_of(s,hero,B.BASE),'cost_after':B.cost_of(s,hero,B.PATCH),'resource':s.resource})
    # Finite passive budgets and min-cost bounds, including deliberately prolonged 50-turn fights.
    findings['passive_regeneration_maximum_per_encounter_50_turns']={f'Invigorate {i}':sum(i for turn in range(1,51) if turn<=3) for i in [1,2,3]}
    findings['post_victory_10_encounters']={'Life Aid':{'HP':50,'SP':20},'Victory Cry':{'HP':100,'SP':50},'stacked_Aid_and_Cry':{'HP':100,'SP':50}}
    # Enumerate survival probabilities for passive counters without re-implementing the engine.
    findings['counter_proc_exact']={name:sum(roll>=dc for roll in range(1,21))/20 for name,dc in [('Counter',19),('Counterstrike',18),('High Counter',17)]}
    findings['affinity_and_guard_on_20_damage']={'normal_guard':8,'resist_guard':4,'weak_guard':12,'null_guard':0,'firm_stance_resist_guard':2}
    findings['Spirit_Drain_conservation']=[{'target_SP':sp,'stolen':min(3,sp),'net_gain_after_1_SP_cost_on_hit':min(3,sp)-1} for sp in range(5)]
    findings['calendar']=[{'days':d,'max_activity_blocks':2*d,'minimum_blocks_rank4_one_social_stat':12,'training_if_all_blocks_train':(2*d)//3,'one_relationship_rank1_to6_blocks':10,'note':'No school bonus or free stat+training double reward.'} for d in [7,30,90]]
    B.dump('focused_rule_audit.json',findings);return findings

if __name__=='__main__':
    import time
    start=time.time();deterministic_families();print('DETERMINISTIC AUDIT COMPLETE',flush=True)
    farm();print('RETREAT FARM TESTS COMPLETE',flush=True)
    despair_combat();print('FULL DESPAIR COMBATS COMPLETE',flush=True)
    price_duels();print('ISOLATED MAGIC DUELS COMPLETE',flush=True)
    reference_traces();B.dump('focused_run.json',{'retreat_trials':12*5000,'despair_combats':6*1800,'price_duels':24*1500,'seconds':round(time.time()-start,2)});print('DONE',round(time.time()-start,2),flush=True)
