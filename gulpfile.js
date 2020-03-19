"use strict";

// Imports
var { src, dest, series } = require("gulp");
var del = require("del");
var sass = require("gulp-sass");

// Vendor settings
sass.compiler = require("node-sass");

// Settings
var settings = {
    clean: true,
    copy: true,
    styles: true
};

// Paths

var paths = {
    input: "website/static/src/",
    output: "website/static/dist/"
};

var copyPaths = {
    input: paths.input + "copy/**/*",
    output: paths.output
};

var stylesPaths = {
    input: paths.input + "scss/**/*.scss",
    output: paths.output + "css/"
};

// Functions

function cleanDist(done) {
    // Make sure this feature is activated before running
    if (!settings.clean) return done();

    // Clean the dist folder
    del.sync([paths.output]);

    // Signal completion
    return done();
}

// Copy static files into output folder
function copyFiles(done) {
    // Make sure this feature is activated before running
    if (!settings.copy) return done();

    // Copy static files
    return src(copyPaths.input).pipe(dest(copyPaths.output));
}

function buildStyles(done) {
    // Make sure this feature is activated before running
    if (!settings.styles) return done();

    // Process styles
    return src(stylesPaths.input)
        .pipe(sass({ outputStyle: "expanded", sourceComments: true }).on('error', sass.logError))
        .pipe(dest(stylesPaths.output));
}

exports.default = series(cleanDist, copyFiles, buildStyles);

exports.cleanDist = cleanDist;
exports.copyFiles = copyFiles;
exports.buildStyles = buildStyles;
