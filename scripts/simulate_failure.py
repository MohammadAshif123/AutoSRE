import argparse, requests
p=argparse.ArgumentParser()
p.add_argument("--type",choices=["crash"],default="crash")
p.add_argument("--url",default="http://127.0.0.1:8000")
a=p.parse_args()
r=requests.post(a.url+"/simulate/failure",json={"type":a.type},timeout=20)
print(r.status_code,r.text)
