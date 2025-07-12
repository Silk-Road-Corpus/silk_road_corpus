const fs = require('fs');
const topojson = require('topojson-client');
const topojsonServer = require('topojson-server');
const { geo2topo } = topojsonServer;

const inputFile = 'tmp/china.topojson';
const outputFile = 'tmp/china_outline.topojson';

const china = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

// Extract the geometries
const geometries = china.objects.CHNADM0gbOpen.geometries;

// Merge the geometries into a single polygon
const merged = topojson.merge(china, geometries);

// Convert back to TopoJSON
const topology = geo2topo({outline: merged});

fs.writeFileSync(outputFile, JSON.stringify(topology));

console.log(`Outline written to ${outputFile}`);
