#!/usr/bin/env node
'use strict';
const meow = require('meow');
const chunk = require('lodash/chunk');
const range = require('lodash/range');
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

const options = {
  description: false,
  help: `
Usage:
  ${path.basename(process.argv[1])} <file> [options]
Options:
  -n --num_frames <frames>  How many frames (collages) to generate. [default: 32]
  -h --help                 Print this message and exit.
`,
  flags: {
    frames: {type: 'number', alias: 'n', default: 32},
    modulate: {type: 'boolean', alias: 'm', default: false}
  }
};

(async cli => {
  if (cli.flags.h) cli.showHelp(0);
  if (cli.input.length < 1) cli.showHelp(2);

  const pwd = process.cwd();
  const input = cli.input.shift();
  const target = path.resolve(pwd, input);
  const files = await readdir(path.resolve(pwd, 'images'));
  const jpegs = files.filter(file => file.endsWith('.jpeg'));
  const sizes = range((jpegs.length - cli.flags.frames), jpegs.length);
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
  for (const subset of chunk(tasks, os.cpus().length)) {
    await Promise.all(subset.map(task => {
      const {size, dir} = task;
      console.log(`${pad(size)} (${pad(tasks.indexOf(task) + 1)}/${sizes.length})`);
      return execFile('python', ['segment.py', size, dir]);
    }));
  }
})(meow(options));
