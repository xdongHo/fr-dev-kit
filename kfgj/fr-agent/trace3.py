import urllib.request, json
events = json.loads(urllib.request.urlopen('http://localhost:18999/events?n=100', timeout=5).read())
# Show only non-MOUSE events and SQL-related
for e in events:
    t = e.get('type', '?')
    if 'MOUSE' not in t and 'FOCUS' not in t:
        comp = e.get('comp', {})
        print(f'{t:25s} cls={comp.get("cls","?")}')
    # Also show any event with SQL/Query/Beautify
    comp = e.get('comp', {})
    cls = comp.get('cls', '')
    if any(kw in cls for kw in ['SQL','Sql','sql','Query','Format','Beaut','TableData']):
        print(f'{t:25s} cls={cls}')
