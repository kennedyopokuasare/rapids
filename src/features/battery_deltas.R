source("renv/activate.R")

library("tidyverse")

battery <- read.csv(snakemake@input[[1]])

if(nrow(battery) > 0){
  consumption <- battery %>%
    mutate(group = ifelse(lag(battery_status) != battery_status, 1, 0) %>% coalesce(0),
           group_id = cumsum(group) + 1) %>%
    filter(battery_status == 2 | battery_status == 3) %>%
    group_by(group_id) %>%
    summarize(battery_diff = first(battery_level) - last(battery_level),
              time_diff = (last(timestamp) - first(timestamp)) / (1000 * 60),
              local_start_date_time = first(local_date_time),
              local_end_date_time = last(local_date_time),
              local_start_date = first(local_date),
              local_end_date = last(local_date),
              local_start_day_segment = first(local_day_segment),
              local_end_day_segment = last(local_day_segment)) %>%
    select(-group_id) %>%
    filter(time_diff > 6) # Avoids including quick cycles
} else {
  consumption <- data.frame(battery_diff = numeric(), 
                            time_diff = numeric(),
                            local_start_date_time = character(),
                            local_end_date_time = character(),
                            local_start_date = character(),
                            local_end_date = character(),
                            local_start_day_segment = character(),
                            local_end_day_segment = character())
}

write.csv(consumption, snakemake@output[[1]], row.names = FALSE)
