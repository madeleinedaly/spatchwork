#!/usr/bin/env node
'use strict';
const chunk = require('lodash.chunk');
const range = require('lodash.range');
const child_process = require('child_process');
const path = require('path');
const util = require('util');
const fs = require('fs');
const os = require('os');

const [mkdir, readdir, copyFile, execFile] = [
  fs.mkdir,
  fs.readdir,
  fs.copyFile,
  child_process.execFile
].map(util.promisify);

(async ([
  frames, // how many collages to make
  input   // base image to collage on
]) => {
  const pwd = process.cwd();
  const concurrency = os.cpus().length;
  const target = path.resolve(pwd, input);
  const files = await readdir(path.resolve(pwd, 'images'));
  const jpegs = files.filter(file => file.endsWith('.jpeg'));
  const sizes = range((jpegs.length - frames), jpegs.length);
  const pad = s => String(s).padStart(sizes[sizes.length - 1].length, '0');

  // create target dirs and copy base image to them in parallel
  const tasks = await Promise.all(sizes.map(async (size, i) => {
    const dir = path.join(pwd, `target-${pad(i)}`);
    await mkdir(dir);
    const dest = path.join(dir, path.parse(input).name);
    await copyFile(target, dest);
    return {size, dir};
  }));

  // generate one collage per core
  for (const subset of chunk(tasks, concurrency)) {
    await Promise.all(subset.map(task => {
      const {size, dir} = task;
      console.log('%s (%s/%d)', pad(size), pad(tasks.indexOf(task)), sizes.length);
      return execFile('python', ['segment.py', size, dir]);
    }));
  }
})(process.argv.slice(2));
