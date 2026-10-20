# SLGA fixtures

Real JSON responses retrieved 20 October 2026 for Dubbo (-32.2569, 148.6011), from the CSIRO-hosted Soil and Landscape Grid of Australia, TERN / ACLEP and collaborators. CC BY 4.0; values are modelled, not field samples.

Each `slga_<code>.json` is the identify response for `https://soils.csiro.au/arcgis/rest/services/TERN/<CODE>_ACLEP_AU_TRN_N/MapServer/identify`. Codes: PHW (pH in water), CLY (clay %), SND (sand %), SOC (carbon %). Parameters select layers 1,2,3,5,6,7,9,10,11 at the point in EPSG:4326, tolerance zero. Raw percent carbon is converted to g/kg by the client.

The service aliases do not expose a release identifier; no release date is inferred. Layer names and retrieval dates are retained in the app's source evidence. Product descriptions: https://esoil.io/TERNLandscapes/Public/Pages/SLGA/ProductDetails-SoilAttributes.html
