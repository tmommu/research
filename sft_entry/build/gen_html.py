import re, sys, html
sys.path.insert(0,'.')
import content as C
TOK=re.compile(r'(\*\*.+?\*\*|\[[^\]]+\])')
def t(s):
    out=[]
    for part in TOK.split(s):
        if not part: continue
        if part.startswith('**'): out.append('<b>'+html.escape(part[2:-2])+'</b>')
        elif part.startswith('['): out.append('<span style="background-color:#ffff00">'+html.escape(part)+'</span>')
        else: out.append(html.escape(part))
    return ''.join(out)
def p(text,label=None):
    return '<p>'+('<b>'+html.escape(label)+'</b>' if label else '')+t(text)+'</p>'
def tbl(rows,hdr=True,boldlast=0):
    o='<table border="1" cellpadding="4" style="border-collapse:collapse">'
    for i,r in enumerate(rows):
        o+='<tr>'
        for c in r:
            tag='th' if (hdr and i==0) else 'td'
            c=t(c)
            if boldlast and i>=len(rows)-boldlast: c='<b>'+c+'</b>'
            o+=f'<{tag} style="text-align:left">{c}</{tag}>'
        o+='</tr>'
    return o+'</table><p></p>'
H='<html><head><meta charset="utf-8"><style>body{font-family:Arial;font-size:11pt;line-height:1.5} h3{font-size:11pt}</style></head><body>'
# proposal
o=H
o+=tbl([("Entrant's school:",C.SCHOOL),("Adviser's name:",C.ADVISER),("Name of team members:",'; '.join(C.TEAM)),("Grade level per member:","Grade 10 (all members)"),("Theme (choose 1):",C.THEME+" (chosen)"),("Entry title:",C.TITLE),("Project description (three sentences):",C.DESC)],hdr=False)
o+='<h3>1. What problem are you trying to solve?</h3>'+''.join(p(x) for x in C.S1)
o+='<h3>2. What do you want to achieve?</h3>'+p(C.GOAL,'Goal: ')+'<p><b>Objectives (SMART):</b></p>'+''.join(p(x,l) for l,x in C.OBJ)
o+='<h3>3. Who will benefit from this project?</h3>'+p(C.S3)
o+='<h3>4. How did you come up with your proposal?</h3>'+p(C.S4_SELECT,'Select. ')+p(C.S4_EXISTS,'What exists. ')+tbl([("Existing work","What it does","What it leaves open")]+C.PRIOR)+p(C.S4_GAP,'Gap we test. ')
o+='<h3>5. How will your tech solution work?</h3>'+p(C.S5_STEM)+'<p><i>Figure 1. How plastic and signals move through the unit. [Insert from the Word file.]</i></p>'+''.join(p(x,l) for l,x in C.S5_STEPS)+'<p><i>Figure 2. Cutaway of the floating SAGIP unit (schematic). [Insert from the Word file.]</i></p>'+p(C.S5_PLAIN,'In plain words. ')
o+='<h3>6. How will you implement this?</h3><p><b>Resources</b></p>'+p('The pilot unit costs about PHP 12,000 and is built in three stages, each bought only after the previous test passes.')+tbl([("Item","PHP")]+C.BUDGET,boldlast=3)+p(C.TOOLS,'Tools. ')+''.join(p(x,l) for l,x in C.STAGES)+p(C.TIMELINE,'Timeline. ')+'<p><b>Stakeholders</b></p>'+''.join(p(x,l) for l,x in C.STAKE)+'<p><b>Risks and mitigation</b></p>'+''.join(p(x,l) for l,x in C.RISKS)
o+='<h3>7. What kind of impact do you hope to achieve and what is the long-term vision for this proposal?</h3>'+p(C.S7_INTRO)+'<p><b>Measurable Outcomes</b></p>'+''.join(p(x,l) for l,x in C.OUTCOMES)+p(C.VISION,'Long-Term Vision: ')+p(C.TAKEAWAY,'Key Takeaway: ')
o+='<h3>References</h3>'+''.join('<p style="font-size:10pt">'+t(r)+'</p>' for r in C.REFS)+'</body></html>'
open('proposal.html','w').write(o)
print(len(o))
