
library(reshape2)
library(ggplot2)
library(data.table)
library(fasttime)
library(xts)
Sys.setenv('TZ'='UTC')
setwd('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/Writings/UoS/plots/')
rootdir <- "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"
home <- "House10.csv"
df <- fread(paste0(rootdir, home))
df_xts <- xts(df$ChestFreezer, fastPOSIXct(df$Time))
df_xts_sub <- resample_UTC_data_minutely(df_xts, 1)

day1 <- df_xts_sub['2014-04-04']
day2 <- df_xts_sub['2014-04-05']
temp <- data.frame(coredata(day1), coredata(day2))
colnames(temp) <-  c('day1','day2')
temp$timestamp = index(day1)
df_long <- reshape2::melt(temp,id.vars = "timestamp")

g <- ggplot(df_long,aes(timestamp,value ,group = variable,color = variable, size = variable)) + geom_line()
g <- g + scale_color_manual(values=c('blue','black')) + scale_size_manual(values=c(0.4, 0.7))
g <- g + theme(legend.position="none",axis.text=element_text(color="black",size=10)) + scale_x_datetime(labels=scales::date_format("%H:%M")) + labs(x= "Hour of the day", y = "Power (W)")
g
#savename <- paste0(inspec_date,"_",strsplit(filename,'[.]')[[1]][1],".pdf")