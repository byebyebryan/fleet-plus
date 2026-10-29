#!/usr/bin/env node
// Owned, temporary browser/server only. No user browser or native agent calls.
import assert from 'node:assert/strict';
import { createReadStream } from 'node:fs';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { chromium } from 'playwright';

const output = path.resolve(process.argv[2] || '');
if (!process.argv[2]) throw new Error('Pass the checked site output directory.');
const mime = {'.html':'text/html', '.css':'text/css', '.js':'text/javascript', '.png':'image/png', '.gif':'image/gif', '.svg':'image/svg+xml', '.json':'application/json', '.mp4':'video/mp4'};
const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    if (!url.pathname.startsWith('/fleet-plus/')) { res.writeHead(404).end(); return; }
    const relative = decodeURIComponent(url.pathname.slice('/fleet-plus/'.length));
    const target = path.resolve(output, relative + (relative.endsWith('/') || !relative ? 'index.html' : ''));
    if (!target.startsWith(output + path.sep)) { res.writeHead(403).end(); return; }
    const type = mime[path.extname(target)] || 'text/plain';
    const stat = await fs.stat(target);
    if (type === 'video/mp4' && req.headers.range) {
      const match = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
      if (!match) { res.writeHead(416, {'Content-Range':`bytes */${stat.size}`}).end(); return; }
      const suffix = match[1] === '';
      const start = suffix ? Math.max(0, stat.size - Number(match[2])) : Number(match[1]);
      const end = suffix || match[2] === '' ? stat.size - 1 : Math.min(stat.size - 1, Number(match[2]));
      if (start > end || start >= stat.size) { res.writeHead(416, {'Content-Range':`bytes */${stat.size}`}).end(); return; }
      res.writeHead(206, {
        'Content-Type':type,
        'Accept-Ranges':'bytes',
        'Content-Range':`bytes ${start}-${end}/${stat.size}`,
        'Content-Length':end - start + 1
      });
      createReadStream(target, {start, end}).pipe(res);
      return;
    }
    const data = await fs.readFile(target);
    res.writeHead(200, {'Content-Type':type, 'Content-Length':stat.size, ...(type === 'video/mp4' ? {'Accept-Ranges':'bytes'} : {})}).end(data);
  } catch { res.writeHead(404).end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}/fleet-plus/`;
let browser;
const errors = [];
try {
  browser = await chromium.launch({headless:true});
  const context = await browser.newContext({reducedMotion:'reduce'});
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  let demoRequests = 0;
  page.on('request', request => { if (request.url().endsWith('/assets/observer-terminal-demo.mp4')) demoRequests++; });
  const catalog = JSON.parse(await fs.readFile(new URL('../data/projects.json', import.meta.url), 'utf8'));
  const routes = ['', 'start/', 'architecture/', 'compatibility/', ...catalog.projects.map(p => `projects/${p.slug}/`)];
  let visits = 0;
  for (const width of [320, 390, 768, 1280]) {
    await page.setViewportSize({width,height:900});
    for (const route of routes) {
      const response = await page.goto(base + route);
      assert.equal(response.status(), 200, route);
      assert.equal(await page.locator('h1').count(), 1);
      assert.equal(await page.locator('main').count(), 1);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `overflow: ${width} ${route}`);
      for (const image of await page.locator('img').all()) await image.scrollIntoViewIfNeeded();
      await page.waitForFunction(() => Array.from(document.images).every(image => image.complete && image.naturalWidth > 0), null, {timeout:10000});
      visits++;
    }
  }
  await page.goto(base + 'projects/agent-observer/');
  await page.getByRole('button', {name:'Partial evidence',exact:true}).click();
  assert.match(await page.locator('[data-scene-text]').innerText(), /cannot establish/);
  assert.equal(await page.locator('[data-scene-status]').getAttribute('data-kind'), 'partial');
  await page.getByRole('button', {name:'Fleet read',exact:true}).click();
  assert.match(await page.locator('[data-scene-title]').innerText(), /fleet/i);
  await page.getByRole('button', {name:'Local read',exact:true}).click();
  assert.equal(await page.locator('button[data-scene][aria-pressed=true]').count(), 1);
  assert((await page.locator('#observer-dashboard').getAttribute('src')).endsWith('dashboard.png'));
  await page.getByRole('button', {name:'Play rendered demo',exact:true}).click();
  assert((await page.locator('#observer-dashboard').getAttribute('src')).endsWith('dashboard.gif'));
  await page.getByRole('button', {name:'Pause rendered demo',exact:true}).click();
  assert((await page.locator('#observer-dashboard').getAttribute('src')).endsWith('dashboard.png'));
  await page.goto(base + 'architecture/');
  for (const [host,expected] of [['Tower','Tower → Laptop'],['Laptop','Laptop → Tower'],['Desk','Desk → Tower · Desk → Laptop']]) {
    await page.getByRole('button', {name:`From ${host}`,exact:true}).click();
    assert.equal(await page.locator('[data-route-list]').innerText(), expected);
  }
  await page.goto(base);
  await page.keyboard.press('Tab');
  assert.equal(await page.locator(':focus').innerText(), 'Skip to content');
  await page.keyboard.press('Enter');
  assert.equal(await page.locator(':focus').getAttribute('id'), 'main');

  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.setViewportSize({width:390,height:900});
  await page.goto(base);
  const terminalImage = page.locator('[data-terminal-poster] img');
  await terminalImage.scrollIntoViewIfNeeded();
  assert((await terminalImage.evaluate(image => image.currentSrc)).endsWith('observer-terminal-compact.png'));
  assert.match(await terminalImage.getAttribute('alt'), /Compact Agent Observer terminal dashboard/);
  const terminalVideo = page.locator('[data-terminal-video]');
  assert.equal(await terminalVideo.getAttribute('preload'), 'none');
  assert.equal(await terminalVideo.getAttribute('autoplay'), null);
  assert.equal(await terminalVideo.isHidden(), true);
  assert.equal(await terminalVideo.evaluate(video => video.controls && video.paused), true);
  assert.equal(demoRequests, 0, 'the terminal demo must not load before opt-in');
  await page.getByRole('button', {name:'Play terminal demo',exact:true}).click();
  assert.equal(await terminalVideo.isVisible(), true);
  await page.waitForFunction(() => {
    const video = document.querySelector('[data-terminal-video]');
    return video && !video.paused && video.currentTime > 0;
  }, null, {timeout:10000});
  assert(demoRequests > 0, 'explicit playback should load the MP4');

  await page.emulateMedia({reducedMotion:'reduce'});
  await page.waitForFunction(() => document.querySelector('[data-terminal-video]')?.paused);
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.waitForTimeout(250);
  assert.equal(await terminalVideo.evaluate(video => video.paused), true, 'reduced motion must not auto-resume');

  await terminalVideo.evaluate(video => video.play());
  await page.waitForFunction(() => !document.querySelector('[data-terminal-video]').paused);
  await page.evaluate(() => {
    Object.defineProperty(document, 'hidden', {configurable:true,value:true});
    document.dispatchEvent(new Event('visibilitychange'));
  });
  await page.waitForFunction(() => document.querySelector('[data-terminal-video]').paused);
  await page.evaluate(() => { delete document.hidden; document.dispatchEvent(new Event('visibilitychange')); });

  await terminalVideo.evaluate(video => video.play());
  await page.waitForFunction(() => !document.querySelector('[data-terminal-video]').paused);
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForFunction(() => document.querySelector('[data-terminal-video]').paused);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(250);
  assert.equal(await terminalVideo.evaluate(video => video.paused), true, 'offscreen return must not auto-resume');

  await page.setViewportSize({width:1280,height:900});
  await page.goto(base);
  await terminalImage.scrollIntoViewIfNeeded();
  assert((await terminalImage.evaluate(image => image.currentSrc)).endsWith('observer-terminal-wide.png'));
  const staticContext = await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:900}});
  const staticPage = await staticContext.newPage();
  await staticPage.goto(base + 'projects/agent-observer/');
  assert.equal(await staticPage.getByRole('heading', {name:'Agent Observer',exact:true}).count(), 1);
  await staticPage.getByText('Read all three cases', {exact:true}).click();
  assert(await staticPage.getByText(/Fleet clients add optional Mesh/).isVisible());
  assert.equal(await staticPage.locator('[data-media-toggle]:visible').count(), 0);
  assert(await staticPage.locator('[data-terminal-poster] img').isVisible());
  assert((await staticPage.locator('[data-terminal-poster] img').evaluate(image => image.currentSrc)).endsWith('observer-terminal-compact.png'));
  assert.equal(await staticPage.locator('[data-terminal-video]').isHidden(), true);
  assert.equal(await staticPage.locator('[data-terminal-toggle]').isHidden(), true);
  assert.equal(await staticPage.getByRole('link', {name:'Watch the terminal demo'}).count(), 1);
  assert((await staticPage.locator('#observer-dashboard').getAttribute('src')).endsWith('dashboard.png'));
  if (process.env.FLEET_SCREENSHOTS) {
    await fs.mkdir(process.env.FLEET_SCREENSHOTS,{recursive:true});
    for (const [name,width,route] of [['home-desktop',1280,''],['home-mobile',390,''],['observer',1280,'projects/agent-observer/'],['architecture',1280,'architecture/']]) {
      await page.setViewportSize({width,height:950});
      await page.goto(base + route);
      await page.screenshot({path:path.join(process.env.FLEET_SCREENSHOTS,name+'.png'),fullPage:true});
    }
  }
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({visits,viewports:4,routes:routes.length,interactions:'observation/routes/motion/keyboard/no-JS',errors}));
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
