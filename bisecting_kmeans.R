idx_t = idx
data = final[,10:19]
rownames(data) = 1:nrow(data)

bisec_kmeans = function(data,k_point){
  rownames(data) = 1:nrow(data)
  idx = matrix(rep(0,nrow(data)),ncol=1)
  idx_now = 1
  meaned = kmeans(data,2)
  var=data.frame(var=c(sort(meaned$withinss)),idx=c(1,2))
  
  idx[which(meaned$cluster==which(meaned$withinss==min(meaned$withinss))),]=idx_now
  ##a = idx[794,]
  for(it in 2:(k_point-1)){
    idx = round(idx)
    idx[which(idx[,1]==which(var$var==max(var$var))),]=0
    
    var = var[!var$var==max(var$var),]
    meaned = kmeans(data[which(idx==0),],2)
    var = rbind(var,c(meaned$withinss[which(meaned$withinss==min(meaned$withinss))],idx_now+1))
    var = rbind(var,c(meaned$withinss[which(meaned$withinss==max(meaned$withinss))],idx_now+2))

    idx[as.numeric(names(which(meaned$cluster==(which(meaned$withinss==min(meaned$withinss)))))),] = idx_now+1
    idx[as.numeric(names(which(meaned$cluster==(which(meaned$withinss==max(meaned$withinss)))))),] = idx_now+2

    #그다음 sorting and reindexing
    var = var[order(var$var),]
    for(k in 1:nrow(var)){
      idx[which(idx==var$idx[k]),]=k+0.1
    }
    idx=idx-0.1
    idx_now = idx_now+1
    for(k in 1:nrow(var)){
      var$idx[k]=k
    }
  }
  return(var)
}

d=c()
for(j in 1:100){
  var=c()
for(i in 3:10){
  var=c(var,bisec_kmeans(data[,10:19],i)[1,1])
  
  }
d = rbind(d,var)
}
ts.plot(colMeans(d))

 # 결론 : 10개의 조합


var=c()
for(i in 3:11){
  var=c(var,bisec_kmeans(data[,10:19],i)[1,1])
}
ts.plot(var)

jump=c()
var_s = scaling(var)
ts.plot(var)

  for(i in 2:8){
    tmp = (var_s[i-1]-var_s[i])/(var_s[i]-var_s[i+1])*i
    jump=c(jump,tmp)
}
ts.plot(jump)
var_s
