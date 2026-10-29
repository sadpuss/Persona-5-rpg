import balance_lab as B
import time

def run(n=75):
    start=time.time();out=[];fights=0
    for i,p in enumerate(B.profiles):
        level=max(1,min(99,p['level']))
        for known in [False,True]:
            for fix in [B.BASE,B.PATCH]:
                results=[]
                for j in range(n):
                    heroes=B.party(level,2,'balanced',fix,advanced=level>=25)
                    foes=[B.make_enemy(p,k) for k in range(3)]
                    f=B.Fight(heroes,foes,1618033+p['number']*1009+j,fix,known,'none')
                    results.append(f.run())
                out.append({'card_number':p['number'],'enemy':p['name'],'level':level,'party_size':2,'enemy_count':3,'known':known,'rules':fix.label,**B.summarize(results)});fights+=n
        if (i+1)%40==0:B.dump('all_cards_partial.json',out);print('CARD COVERAGE',i+1,'/',len(B.profiles),flush=True)
    assert {r['card_number'] for r in out}=={p['number'] for p in B.profiles}
    B.dump('all_cards_matrix.json',out);B.dump('all_cards_run.json',{'profiles':len(B.profiles),'fights':fights,'cells':len(out),'seconds':round(time.time()-start,2)})
    print('ALL CARD TESTS COMPLETE',fights,flush=True)
if __name__=='__main__':run()
