#!/usr/bin/env node
'use strict';
const {mkdir, readdir, copyFile} = require('fs');
const {execFile} = require('child_process');
const util = require('util');
const path = require('path');

const [
  mkdirAsync,
  readdirAsync,
  copyFileAsync,
  execFileAsync
] = [mkdir, readdir, copyFile, execFile].map(util.promisify);

const all = Promise.all.bind(Promise);
const range = (beg, end) => [...Array(1 + end - beg).keys()].map(v => beg + v);

(async ([input]) => {
  const NUM_FRAMES = 420;
  const pwd = process.cwd();
  const target = path.resolve(pwd, input);
  const files = await readdirAsync(path.resolve(pwd, 'images'));
  const jpegs = files.filter(file => file.endsWith('.jpeg'));
  const sizes = range((jpegs.length - NUM_FRAMES), jpegs.length);
  const dirs = [];

  await all(sizes.map((_, i) => {
    const dir = path.join(pwd, `target-${i}/`);
    dirs.push(dir);
    return mkdirAsync(dir);
  }));

  await all(dirs.map(dir => copyFileAsync(target, path.join(dir, path.parse(input).name))));
  await all(dirs.map((dir, i) => execFileAsync('python', ['segment.py', sizes[i], dir])));
})(process.argv.slice(2));
