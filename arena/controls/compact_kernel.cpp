// Bounded numeric implementation of the reference engine, shared random rankings.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <numeric>
#include <random>
#include <vector>
#include <omp.h>
extern "C" void evaluate(
 int count, int first_id, int base_seed, int U, int C, int D, int S, int H,
 const int* cycle_ids, const int* universe, const int* sizes, const int* rebalance,
 const int* starts, const int* ends, const int* ks, const int* drops,
 const double* opening, const double* marks, const uint8_t* buy_ok, const uint8_t* sell_ok,
 double initial, int lot, int fractional, double buy_fee, double sell_fee, double minimum,
 double* cash_state, int* held_ids, double* quantities,
 double* returns, double* weekly_nav, int threads) {
 omp_set_num_threads(threads);
 #pragma omp parallel for schedule(static)
 for(int m=0;m<count;++m){
  std::vector<std::vector<int>> ranked(C);
  std::vector<std::vector<double>> scores(C,std::vector<double>(U,-1));
  for(int c=0;c<C;++c){
   if(!rebalance[c]) continue;
   uint64_t id=static_cast<uint64_t>(first_id+m);
   uint32_t seed=(base_seed+id*10007+static_cast<uint64_t>(cycle_ids[c])*37)%2147483647;
   std::mt19937 rng(seed);
   for(int j=0;j<sizes[c];++j){
    int i=universe[c*U+j];
    uint32_t a=rng()>>5, b=rng()>>6;
    scores[c][i]=(a*67108864.0+b)/9007199254740992.0;
    ranked[c].push_back(i);
   }
   std::stable_sort(ranked[c].begin(),ranked[c].end(),[&](int a,int b){return scores[c][a]>scores[c][b];});
  }
  int offset=0;
  for(int s=0;s<S;++s){
   int K=ks[s]; double cash=cash_state[m*S+s];
   std::vector<double> held(U,0);
   for(int j=0;j<K;++j){int i=held_ids[m*H+offset+j]; if(i>=0) held[i]=quantities[m*H+offset+j];}
   for(int c=0;c<C;++c){
    if(rebalance[c]){
     std::vector<int> current, candidates, out, inside, sells, buys;
     for(int i=0;i<U;++i) if(held[i]>0) current.push_back(i);
     int effective=std::min(K,sizes[c]);
     double budget=(current.empty()?cash*.995:initial)/std::max(effective,1);
     for(int i:ranked[c]){
      double p=opening[c*U+i];
      if(!buy_ok[c*U+i] || !std::isfinite(p) || p<=0) continue;
      if(!fractional && held[i]<=0 && p*lot>budget) continue;
      candidates.push_back(i);
     }
     int capacity=std::min(K,static_cast<int>(candidates.size()));
     if(current.empty()){
      buys.assign(candidates.begin(),candidates.begin()+capacity);
     } else {
      std::vector<uint8_t> target(U,0);
      for(int j=0;j<capacity;++j) target[candidates[j]]=1;
      for(int i:current){
       if(!sell_ok[c*U+i] || !std::isfinite(opening[c*U+i]) || opening[c*U+i]<=0) continue;
       if(scores[c][i]<0) out.push_back(i); else inside.push_back(i);
      }
      for(int j=0;j<std::min(drops[s],static_cast<int>(out.size()));++j) sells.push_back(out[j]);
      std::sort(inside.begin(),inside.end(),[&](int a,int b){
       if(target[a]!=target[b]) return target[a]<target[b];
       if(scores[c][a]!=scores[c][b]) return scores[c][a]<scores[c][b];
       return a<b;
      });
      int entrants=0; for(int j=0;j<capacity;++j) if(held[candidates[j]]<=0) ++entrants;
      int active=std::min({drops[s]-static_cast<int>(sells.size()),entrants,static_cast<int>(inside.size())});
      for(int j=0;j<active;++j) sells.push_back(inside[j]);
      int need=std::max(0,capacity-static_cast<int>(current.size())+static_cast<int>(sells.size()));
      for(int i:candidates){
       if(static_cast<int>(buys.size())>=need) break;
       if(held[i]<=0 || std::find(sells.begin(),sells.end(),i)!=sells.end()) buys.push_back(i);
      }
     }
     for(int i:sells){double p=opening[c*U+i]; if(!std::isfinite(p)||p<=0) continue;
      double value=held[i]*p; cash+=value-std::max(value*sell_fee,minimum); held[i]=0;
     }
     double per=buys.empty()?0:cash*.995/buys.size();
     for(int i:buys){double p=opening[c*U+i];
      if(!buy_ok[c*U+i]||!std::isfinite(p)||p<=0) continue;
      double qty=fractional?per/p:std::floor(per/(p*lot))*lot;
      if(qty<(fractional?1:lot)) continue;
      double value=qty*p, spent=value+std::max(value*buy_fee,minimum);
      if(spent<=cash){cash-=spent; held[i]+=qty;}
     }
    }
    double nav=1;
    for(int d=starts[c];d<ends[c];++d){
     double value=cash; for(int i=0;i<U;++i) if(held[i]>0) value+=held[i]*marks[d*U+i];
     nav=value/initial;
    }
    weekly_nav[(m*S+s)*C+c]=nav;
   }
   cash_state[m*S+s]=cash;
   for(int j=0;j<K;++j){held_ids[m*H+offset+j]=-1; quantities[m*H+offset+j]=0;}
   int j=0; for(int i=0;i<U;++i) if(held[i]>0){
    if(j<K){held_ids[m*H+offset+j]=i; quantities[m*H+offset+j]=held[i];++j;}
   }
   returns[m*S+s]=weekly_nav[(m*S+s)*C+C-1]-1;
   offset+=K;
  }
 }
}
