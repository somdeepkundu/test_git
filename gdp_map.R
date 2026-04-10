# ============================================================
# GDP per Capita Animated Choropleth Map — v9
# Equal Earth projection + boundary lines + Box-Cox
# ============================================================

setwd(here::here())

library(here)
library(ggplot2)
library(gganimate)
library(sf)
library(maps)
library(dplyr)
library(gifski)
library(gapminder)
library(scales)
library(MASS)

# ── 1. Projection ────────────────────────────────────────────────────────────

eqearth_crs <- "+proj=eqearth +datum=WGS84 +units=m +no_defs"

# ── 2. Data Preparation ──────────────────────────────────────────────────────

world_sf <- sf::st_as_sf(maps::map("world", plot = FALSE, fill = TRUE))

gapminder_clean <- gapminder %>%
  mutate(country = as.character(country)) %>%
  mutate(country = recode(country,
    "United States"           = "USA",
    "United Kingdom"          = "UK",
    "Korea, Rep."             = "South Korea",
    "Korea, Dem. Rep."        = "North Korea",
    "Congo, Dem. Rep."        = "Democratic Republic of the Congo",
    "Congo, Rep."             = "Republic of Congo",
    "Trinidad and Tobago"     = "Trinidad",
    "Yemen, Rep."             = "Yemen",
    "Cote d'Ivoire"           = "Ivory Coast",
    "Slovak Republic"         = "Slovakia",
    "West Bank and Gaza"      = "Palestine"
  ))

# Join + pre-transform to Equal Earth (so gganimate can't drop the projection)
world_gdp_sf <- world_sf %>%
  left_join(
    gapminder_clean %>% dplyr::select(country, year, gdpPercap),
    by           = c("ID" = "country"),
    relationship = "many-to-many"
  ) %>%
  sf::st_transform(eqearth_crs)

# ── 3. Box-Cox Transformation ────────────────────────────────────────────────

gdp_vals <- gapminder_clean$gdpPercap[
  !is.na(gapminder_clean$gdpPercap) & gapminder_clean$gdpPercap > 0
]
bc_fit <- MASS::boxcox(lm(gdp_vals ~ 1),
                        lambda = seq(-1, 1, 0.01),
                        plotit = FALSE)
lambda <- round(bc_fit$x[which.max(bc_fit$y)], 2)
message(sprintf("Optimal Box-Cox lambda: %.2f", lambda))

bc_trans <- scales::trans_new(
  name      = paste0("boxcox_", lambda),
  transform = function(x) if (lambda == 0) log(x) else (x^lambda - 1) / lambda,
  inverse   = function(x) if (lambda == 0) exp(x) else (x * lambda + 1)^(1 / lambda),
  domain    = c(1e-6, Inf)
)

# ── 4. Globe + Graticule (pre-transformed to Equal Earth) ────────────────────

globe_ee <- sf::st_as_sfc(
  "POLYGON((-179.9 -89.9, 179.9 -89.9, 179.9 89.9, -179.9 89.9, -179.9 -89.9))",
  crs = 4326
) %>% sf::st_transform(eqearth_crs)

grat_ee <- sf::st_graticule(
  lon    = seq(-180, 180, by = 30),
  lat    = seq(-90,   90, by = 30),
  ndiscr = 100
) %>% sf::st_transform(eqearth_crs)

# ── 5. Year Progress Bar (Equal Earth meters) ────────────────────────────────

years_seq <- sort(unique(gapminder_clean$year))
year_min  <- min(years_seq)
year_max  <- max(years_seq)

bar_xmin_m <-  -14e6
bar_xmax_m <-   14e6
bar_y_m    <-   -9.8e6

marker_df <- data.frame(
  year     = years_seq,
  marker_x = bar_xmin_m +
    (years_seq - year_min) / (year_max - year_min) * (bar_xmax_m - bar_xmin_m)
)

# ── 6. Build Plot ─────────────────────────────────────────────────────────────

p <- ggplot() +

  # Ocean globe fill + outline
  geom_sf(data = globe_ee, fill = "#c6e8f5", color = "grey40", linewidth = 0.3) +

  # Graticule grid
  geom_sf(data = grat_ee, color = "grey80", linewidth = 0.15, alpha = 0.5) +

  # Country polygons with visible boundary lines
  geom_sf(data = world_gdp_sf,
          aes(fill = gdpPercap),
          color = "grey25", linewidth = 0.08) +

  # Progress bar track
  annotate("segment",
           x = bar_xmin_m, xend = bar_xmax_m,
           y = bar_y_m,    yend = bar_y_m,
           color = "grey65", linewidth = 2.5) +

  # Year labels
  annotate("text", x = bar_xmin_m, y = bar_y_m - 5e5,
           label = as.character(year_min),
           size = 3, hjust = 0.5, color = "grey35") +
  annotate("text", x = bar_xmax_m, y = bar_y_m - 5e5,
           label = as.character(year_max),
           size = 3, hjust = 0.5, color = "grey35") +

  # Moving year tick
  geom_segment(
    data = marker_df,
    aes(x = marker_x, xend = marker_x,
        y = bar_y_m - 3e5, yend = bar_y_m + 3e5,
        group = year),
    color = "black", linewidth = 1
  ) +

  scale_fill_viridis_c(
    option   = "plasma",
    trans    = bc_trans,
    labels   = dollar_format(),
    na.value = "grey80",
    name     = "GDP per Capita"
  ) +
  coord_sf(
    xlim   = c(-17.5e6, 17.5e6),
    ylim   = c(-10.5e6, 9e6),
    expand = FALSE
  ) +
  theme_void() +
  theme(
    plot.title       = element_text(size = 16, face = "bold",  hjust = 0.5),
    plot.subtitle    = element_text(size = 13, hjust = 0.5,    color = "grey30"),
    legend.position  = "bottom",
    legend.key.width = unit(2.5, "cm"),
    plot.caption     = element_text(size = 8,  hjust = 0.5,    color = "grey50"),
    plot.margin      = margin(10, 10, 20, 10)
  ) +
  labs(
    title    = "Global GDP per Capita",
    subtitle = "Year: {closest_state}",
    caption  = sprintf(
      "Source: Gapminder  |  Grey = no data  |  Box-Cox \u03bb = %.2f", lambda
    )
  ) +
  transition_states(year, transition_length = 3, state_length = 2) +
  ease_aes("sine-in-out")

# ── 7. Render & Save ──────────────────────────────────────────────────────────

animate(
  p,
  nframes  = 180,
  fps      = 10,
  width    = 1200,
  height   = 650,
  res      = 150,
  renderer = gifski_renderer()
)

anim_save(here("gdp_map_v9.gif"))
