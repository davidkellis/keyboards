#include <bits/stdc++.h>
using namespace std;
struct Node{int f,g,id;bool operator<(const Node&o)const{return f>o.f;}};
int main(int argc,char**v){
 if(argc!=8)return 2;int w=atoi(v[1]),h=atoi(v[2]),sx=atoi(v[3]),sy=atoi(v[4]),tx=atoi(v[5]),ty=atoi(v[6]),N=w*h;
 vector<unsigned char>b(4*N);ifstream in(v[7],ios::binary);in.read((char*)b.data(),b.size());int s=sy*w+sx,t=ty*w+tx;if(b[s]||b[t])return 3;
 vector<int>d(3*N,INT_MAX),prev(3*N,-1);priority_queue<Node>q;
 auto heu=[&](int x,int y,int l){int a=abs(x-tx),c=abs(y-ty);return 10*max(a,c)+4*min(a,c)+(l?150:0);};
 d[s]=0;q.push({heu(sx,sy,0),0,s});int dx[]={-1,1,0,0,-1,-1,1,1},dy[]={0,0,-1,1,-1,1,-1,1};
 while(!q.empty()){
 auto n=q.top();q.pop();if(n.g!=d[n.id])continue;
 if(n.id==t){vector<int>p;for(int z=t;z!=-1;z=prev[z])p.push_back(z);reverse(p.begin(),p.end());for(int z:p)cout<<(z%N)%w<<' '<<(z%N)/w<<' '<<z/N<<'\n';return 0;}
 int pos=n.id%N,l=n.id/N,x=pos%w,y=pos/w;
 auto add=[&](int id,int g,int a,int c,int ll){if(g<d[id]){d[id]=g;prev[id]=n.id;q.push({g+heu(a,c,ll),g,id});}};
 for(int i=0;i<8;i++){int a=x+dx[i],c=y+dy[i];if(a<0||c<0||a>=w||c>=h)continue;int id=l*N+c*w+a;if(b[id]||(i>=4&&(b[l*N+y*w+a]||b[l*N+c*w+x])))continue;add(id,n.g+(i<4?10:14),a,c,l);}
 if(!b[3*N+pos])for(int ll=0;ll<3;ll++)if(ll!=l&&!b[ll*N+pos])add(ll*N+pos,n.g+150,x,y,ll);
 }return 4;
}
