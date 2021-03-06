source("renv/activate.R")

library(tidyr)
library(purrr)
library(dplyr)
library(stringr)

feature_files  <- snakemake@input[["feature_files"]]


features_of_all_participants <- tibble(filename = feature_files) %>% # create a data frame
  mutate(file_contents = map(filename, ~ read.csv(., stringsAsFactors = F, colClasses = c(local_date = "character"))),
         pid = str_match(filename, ".*/([a-zA-Z]+?[0-9]+?)/.*")[,2]) %>%
  unnest(cols = c(file_contents)) %>%
  select(-filename)

write.csv(features_of_all_participants, snakemake@output[[1]], row.names = FALSE)