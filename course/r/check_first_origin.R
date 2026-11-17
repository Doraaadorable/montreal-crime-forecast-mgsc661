# MGSC 661 independent check: refit ETS and ARIMA with the course's R workflow (Lab 10, fpp2)
# at the first backtest origin (data up to December 2019) and compare with Python.
#
# Status: written for a group member to run and check. Not yet run: R is not installed
# in the environment where it was written.
#
# Run from the repository root:
#   Rscript course/r/check_first_origin.R
# Needs: install.packages("fpp2")
#
# Writes course/r/r_first_origin_structures.csv and one checkresiduals() plot per model
# in course/r/plots/. Compare with results/course/structure_selected_origins.csv and
# results/course/residual_checks_first_origin.csv (origin 2019-12-01).
#
# This is an independent check of the method. The reported diagnostics stay those of the
# statsforecast models that produced the backtest forecasts. R's ets() and auto.arima()
# follow similar selection rules, but search ranges, defaults and estimation differ, so R may
# choose another structure. If it does, report the difference and the likely setting behind
# it; do not replace the Python results with the R ones.

library(fpp2)

data <- read.csv("course/r/citywide_monthly_2026-11-15.csv", check.names = FALSE)
categories <- setdiff(names(data), "month")
dir.create("course/r/plots", showWarnings = FALSE)

rows <- list()
for (cat in categories) {
  y <- ts(data[[cat]], start = c(2015, 1), frequency = 12)
  train <- window(y, end = c(2019, 12))   # 60 months, the first origin

  fit.ets <- ets(train)
  fit.arima <- auto.arima(train)
  cat("\n=====", cat, "=====\n")
  print(summary(fit.ets))
  print(summary(fit.arima))

  for (m in list(list(name = "ETS", fit = fit.ets), list(name = "ARIMA", fit = fit.arima))) {
    png(file.path("course/r/plots", paste0(gsub(" ", "_", cat), "_", m$name, ".png")),
        width = 1400, height = 900, res = 150)
    lb <- checkresiduals(m$fit)   # residual plot, ACF, histogram and Ljung-Box, as in class
    dev.off()
    rows[[length(rows) + 1]] <- data.frame(
      category = cat, model = m$name,
      structure = if (m$name == "ETS") m$fit$method else as.character(m$fit),
      ljung_box_statistic = unname(lb$statistic),
      ljung_box_df = unname(lb$parameter),
      ljung_box_p = lb$p.value)
  }
}

out <- do.call(rbind, rows)
write.csv(out, "course/r/r_first_origin_structures.csv", row.names = FALSE)
print(out)
