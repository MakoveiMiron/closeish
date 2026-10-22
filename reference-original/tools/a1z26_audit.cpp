// CLOSEISH A1Z26 full-corpus scorer and independent score-distribution auditor.
// Usage: ./a1z26_audit input.tsv output.tsv target [audit.csv]
// Input:   lowercase_word<TAB>source_mask (1=CMU,2=SCOWL-Hunspell,3=both)
// Output:  lowercase_word<TAB>value<TAB>points<TAB>tier<TAB>source_mask
// Time:    O(total letter count), memory O(N) solely for distribution audit.
// Requires C++17; no external dependencies.
#include <algorithm>
#include <array>
#include <charconv>
#include <chrono>
#include <cstddef>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <vector>
using namespace std;
struct Rec { string word; int sum; int mask; };
static int wordValue(const string& s) {
    int sum = 0;
    if(s.empty()) throw runtime_error("Empty dictionary entry");
    for(unsigned char c : s) {
        if(c >= 'a' && c <= 'z') sum += c - 'a' + 1;
        else if(c >= 'A' && c <= 'Z') sum += c - 'A' + 1;
        else throw runtime_error("Non A-Z letter in dictionary headword: " + s);
    }
    return sum;
}
static pair<int,string> classify(int value,int target){
    int gap = target-value; // from BELOW
    if(gap == 0) return {1200,"PERFECT HIT"};
    if(gap < 0) return {0,"CROSSED LIMIT"};
    if(gap <= 3) return {1000,"RAZOR EDGE"};
    if(gap <= 8) return {800,"CLOSE CALL"};
    if(gap <= 15) return {600,"SOLID HIT"};
    if(gap <= 24) return {400,"IN THE ZONE"};
    if(gap <= 39) return {200,"ON THE BOARD"};
    return {0,"TOO FAR"};
}
static array<int,7> countPoints(const vector<int>& hist,int target){
    array<int,7> out{};
    for(size_t val=0;val<hist.size();val++){
        int p=classify(int(val),target).first;
        int i=p==1200?0:p==1000?1:p==800?2:p==600?3:p==400?4:p==200?5:6;
        out[i]+=hist[val];
    }
    return out;
}
int main(int argc,char**argv){
    if(argc < 4 || argc > 5){
        cerr << "Usage: a1z26_audit input.tsv output.tsv target [audit.csv]\n";
        return 2;
    }
    const auto began=chrono::steady_clock::now();
    string inPath=argv[1], outPath=argv[2];
    int target=0;
    try {target=stoi(argv[3]);}catch(...) {cerr << "Invalid target\n";return 2;}
    if(target<50 || target>5000){cerr<<"Target must be 50..5000\n";return 2;}
    ifstream in(inPath);
    if(!in){cerr<<"Cannot read "<<inPath<<"\n";return 1;}
    ofstream out(outPath);
    if(!out){cerr<<"Cannot write "<<outPath<<"\n";return 1;}
    vector<int> hist(1,0);
    unordered_set<string> uniques;
    vector<string> perfect;
    size_t count=0, letters=0;
    string line;
    while(getline(in,line)){
        if(!line.empty() && line.back()=='\r') line.pop_back();
        if(line.empty()) continue;
        size_t tab=line.find('\t');
        if(tab==string::npos){cerr<<"Missing tab on row "<<count+1<<"\n";return 1;}
        string word=line.substr(0,tab);
        string source=line.substr(tab+1);
        int mask=0;
        auto [end,err]=from_chars(source.data(),source.data()+source.size(),mask);
        if(err!=errc{} || end!=source.data()+source.size() || mask<1 || mask>3){
            cerr<<"Invalid source mask for "<<word<<"\n";return 1;
        }
        if(!uniques.insert(word).second){cerr<<"Duplicate: "<<word<<"\n";return 1;}
        int val=0;
        try{val=wordValue(word);}catch(const exception&ex){cerr<<ex.what()<<'\n';return 1;}
        if(val >= int(hist.size()))hist.resize(val+1,0);
        hist[val]++;
        auto [points,tier]=classify(val,target);
        if(points==1200)perfect.push_back(word);
        out<<word<<'\t'<<val<<'\t'<<points<<'\t'<<tier<<'\t'<<mask<<'\n';
        count++;letters+=word.size();
    }
    out.flush();
    auto d=countPoints(hist,target);
    const int scores[7]={1200,1000,800,600,400,200,0};
    cout << "words="<<count<<" letters="<<letters<<" target="<<target<<"\n";
    for(int i=0;i<7;i++)cout<<scores[i]<<"="<<d[i]<<" ";
    cout<<"\nperfect_words:";
    for(auto&s:perfect)cout<<' '<<s;
    cout<<"\n";
    cout<<"distribution candidates (target 200..230):\n";
    for(int t=250;t<=350;t++){
        auto a=countPoints(hist,t);
        if(a[0]>=1 && a[0]<=5)
            cout<<t<<" perfect="<<a[0]<<" razor="<<a[1]<<" close="<<a[2]<<" solid="<<a[3]<<" zone="<<a[4]<<" board="<<a[5]<<'\n';
    }
    if(argc==5){
        ofstream audit(argv[4]);
        audit<<"target,1200,1000,800,600,400,200,0,total\n";
        for(int t=150;t<=400;t++){
            auto a=countPoints(hist,t);
            audit<<t;
            for(int x:a)audit<<','<<x;
            audit<<','<<count<<'\n';
        }
    }
    auto ms=chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now()-began).count();
    cout<<"time_ms="<<ms<<'\n';
    return 0;
}
