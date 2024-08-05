import { Viewer, CzmlDataSource, Ion } from 'cesium';

// Initialize Cesium Viewer
const viewer = new Viewer('cesiumContainer', {
    shouldAnimate: true
});

// CZML file URL (adjust path as necessary)
const czmlUrl = 'czml_files/czml_output.czml';

// Load CZML data
const czmlDataSource = new CzmlDataSource();
viewer.dataSources.add(czmlDataSource);

czmlDataSource.load(czmlUrl).then(() => {
    viewer.zoomTo(czmlDataSource);
}).otherwise((error) => {
    console.error('Error loading CZML data:', error);
});
