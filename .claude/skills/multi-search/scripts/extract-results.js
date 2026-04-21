// 多平台搜索结果提取脚本
// 自动识别当前页面并使用对应的提取策略

/**
 * 自动识别当前页面类型
 * @returns {string} 平台标识
 */
function detectPlatform() {
  const host = window.location.hostname.replace('www.', '');
  const platformMap = {
    'bing.com': 'bing',
    'cn.bing.com': 'bing',
    'google.com': 'google',
    'google.com.hk': 'google',
    'medium.com': 'medium',
    'twitter.com': 'twitter',
    'x.com': 'twitter',
    'producthunt.com': 'producthunt',
    'news.ycombinator.com': 'hackernews',
    'sspai.com': 'sspai',
    'uxdesign.cc': 'medium',
    'hackernoon.com': 'medium',
  };

  for (const [domain, platform] of Object.entries(platformMap)) {
    if (host.includes(domain.replace('www.', ''))) return platform;
  }
  return 'generic';
}

/**
 * Bing 搜索结果提取
 */
function extractBing(max) {
  const results = [];
  const items = document.querySelectorAll('#b_results > li');

  items.forEach((item, i) => {
    if (i >= max) return;
    const titleEl = item.querySelector('h2 a') || item.querySelector('.b_tpcn h2 a');
    const title = titleEl ? titleEl.textContent.trim() : '';
    let url = titleEl ? titleEl.href : '';

    if (url && url.includes('u=')) {
      const match = url.match(/[?&]u=([^&]+)/);
      if (match) {
        let b64 = match[1];
        while (b64.length % 4) b64 += '=';
        try { url = atob(b64); } catch(e) {}
      }
    }

    let description = '';
    for (const sel of ['.b_lineclamp2', '.b_lineclamp3', '.b_caption p', '.b_desc']) {
      const el = item.querySelector(sel);
      if (el && el.textContent.trim()) { description = el.textContent.trim(); break; }
    }

    let site = '';
    const siteEl = item.querySelector('.tptt') || item.querySelector('.b_attribution cite');
    if (siteEl) site = siteEl.textContent.trim().split('›')[0].trim();

    let date = '';
    const dateEl = item.querySelector('.b_snippetTime');
    if (dateEl) date = dateEl.textContent.trim();

    if (title && !title.includes('的相关搜索')) {
      results.push({ title, url, description, site, date, platform: 'bing' });
    }
  });
  return results;
}

/**
 * Google 搜索结果提取
 */
function extractGoogle(max) {
  const results = [];
  const items = document.querySelectorAll('#search .g, #rso .g');

  items.forEach((item, i) => {
    if (i >= max) return;
    const titleEl = item.querySelector('h3');
    const linkEl = item.querySelector('a[href^="http"]');
    const descEl = item.querySelector('[data-sncf], .VwiC3b, [style*="-webkit-line-clamp"]');
    const dateEl = item.querySelector('.LEwnzc, .f');

    if (titleEl) {
      results.push({
        title: titleEl.textContent.trim(),
        url: linkEl ? linkEl.href : '',
        description: descEl ? descEl.textContent.trim() : '',
        site: linkEl ? new URL(linkEl.href).hostname : '',
        date: dateEl ? dateEl.textContent.trim() : '',
        platform: 'google',
      });
    }
  });
  return results;
}

/**
 * Medium / UX Collective 文章列表提取
 */
function extractMedium(max) {
  const results = [];
  const articles = document.querySelectorAll('article, [data-testid="post-preview"]');

  if (articles.length === 0) {
    const links = document.querySelectorAll('a[data-action="open-post"], a[href*="medium.com/"]');
    links.forEach((link, i) => {
      if (i >= max) return;
      const title = link.textContent.trim();
      if (title && title.length > 10) {
        results.push({
          title,
          url: link.href,
          description: '',
          site: 'Medium',
          date: '',
          platform: 'medium',
        });
      }
    });
    return results;
  }

  articles.forEach((article, i) => {
    if (i >= max) return;
    const titleEl = article.querySelector('h2, h3, [data-testid="post-preview-title"]');
    const linkEl = article.querySelector('a[href*="medium.com"], a[data-action="open-post"]') || article.querySelector('a');
    const descEl = article.querySelector('h3 + p, [data-testid="post-preview-subtitle"]');
    const authorEl = article.querySelector('[data-testid="authorName"], a[data-action="show-user-card"]');
    const dateEl = article.querySelector('time, [datetime]');

    if (titleEl) {
      results.push({
        title: titleEl.textContent.trim(),
        url: linkEl ? linkEl.href : '',
        description: descEl ? descEl.textContent.trim().slice(0, 300) : '',
        site: authorEl ? authorEl.textContent.trim() : 'Medium',
        date: dateEl ? (dateEl.getAttribute('datetime') || dateEl.textContent.trim()) : '',
        platform: 'medium',
      });
    }
  });
  return results;
}

/**
 * Twitter/X 推文提取
 */
function extractTwitter(max) {
  const results = [];
  const tweets = document.querySelectorAll('article[data-testid="tweet"], [data-testid="cellInnerDiv"]');

  tweets.forEach((tweet, i) => {
    if (i >= max) return;

    const textEl = tweet.querySelector('[data-testid="tweetText"]');
    const userEl = tweet.querySelector('[data-testid="User-Name"] a, a[role="link"][href*="/"]');
    const timeEl = tweet.querySelector('time');
    const linkEl = tweet.querySelector('a[href*="/status/"]');

    if (textEl) {
      const text = textEl.textContent.trim();
      results.push({
        title: text.slice(0, 120) + (text.length > 120 ? '...' : ''),
        url: linkEl ? linkEl.href : '',
        description: text,
        site: userEl ? userEl.textContent.trim().split('\n')[0] : 'Twitter',
        date: timeEl ? timeEl.getAttribute('datetime') : '',
        platform: 'twitter',
      });
    }
  });
  return results;
}

/**
 * Product Hunt 产品列表提取
 */
function extractProductHunt(max) {
  const results = [];

  // 尝试多种选择器
  const cards = document.querySelectorAll(
    '[data-test^="post-item"], a[href^="/posts/"]'
  );

  const seen = new Set();
  cards.forEach((card, i) => {
    if (results.length >= max) return;

    let title = '', url = '', description = '';

    if (card.tagName === 'A') {
      title = card.textContent.trim();
      url = card.href;
    } else {
      const titleEl = card.querySelector('a[data-test="post-name"], h3');
      const descEl = card.querySelector('[data-test="post-tagline"], p');
      const linkEl = card.querySelector('a[href^="/posts/"]');

      title = titleEl ? titleEl.textContent.trim() : '';
      description = descEl ? descEl.textContent.trim() : '';
      url = linkEl ? linkEl.href : '';
    }

    if (url && !url.startsWith('http')) url = 'https://www.producthunt.com' + url;
    if (title && title.length > 3 && !seen.has(url)) {
      seen.add(url);
      results.push({
        title,
        url,
        description,
        site: 'Product Hunt',
        date: new Date().toISOString().split('T')[0],
        platform: 'producthunt',
      });
    }
  });
  return results;
}

/**
 * Hacker News 提取
 */
function extractHackerNews(max) {
  const results = [];
  const rows = document.querySelectorAll('tr.athing');

  rows.forEach((row, i) => {
    if (i >= max) return;
    const titleEl = row.querySelector('td.title > span.titleline > a');
    if (!titleEl) return;

    let url = titleEl.href;
    if (url.startsWith('item?')) url = 'https://news.ycombinator.com/' + url;

    // 获取分数和评论数（在下一行）
    const subRow = row.nextElementSibling;
    let score = '', comments = '', age = '';
    if (subRow) {
      const scoreEl = subRow.querySelector('.score');
      const ageEl = subRow.querySelector('.age');
      score = scoreEl ? scoreEl.textContent.trim() : '';
      age = ageEl ? ageEl.textContent.trim() : '';

      const links = subRow.querySelectorAll('a');
      links.forEach(a => {
        if (a.textContent.includes('comment')) comments = a.textContent.trim();
      });
    }

    results.push({
      title: titleEl.textContent.trim(),
      url,
      description: [score, comments].filter(Boolean).join(' | '),
      site: url ? new URL(url).hostname.replace('www.', '') : 'news.ycombinator.com',
      date: age,
      platform: 'hackernews',
    });
  });
  return results;
}

/**
 * 少数派 (sspai.com) 提取
 */
function extractSspai(max) {
  const results = [];
  const articles = document.querySelectorAll('.articleCard, .listItem, article');

  articles.forEach((article, i) => {
    if (i >= max) return;
    const titleEl = article.querySelector('h2, h3, .title, a.title');
    const linkEl = article.querySelector('a[href*="/post/"]') || article.querySelector('a');
    const descEl = article.querySelector('.summary, .desc, p');
    const authorEl = article.querySelector('.author, .nickname');

    if (titleEl) {
      let url = linkEl ? linkEl.href : '';
      if (url && !url.startsWith('http')) url = 'https://sspai.com' + url;

      results.push({
        title: titleEl.textContent.trim(),
        url,
        description: descEl ? descEl.textContent.trim().slice(0, 300) : '',
        site: authorEl ? authorEl.textContent.trim() : '少数派',
        date: '',
        platform: 'sspai',
      });
    }
  });
  return results;
}

/**
 * 通用页面提取（降级方案）
 */
function extractGeneric(max) {
  const results = [];
  const headings = document.querySelectorAll('h1 a, h2 a, h3 a, article a[href]');
  const seen = new Set();

  headings.forEach((el, i) => {
    if (results.length >= max) return;
    const title = el.textContent.trim();
    const url = el.href;

    if (title && title.length > 10 && url && !seen.has(url) && url.startsWith('http')) {
      seen.add(url);
      results.push({
        title,
        url,
        description: '',
        site: new URL(url).hostname,
        date: '',
        platform: 'generic',
      });
    }
  });
  return results;
}

// ============================================================
// 主入口
// ============================================================

/**
 * 统一提取入口：自动识别平台并提取结果
 * @param {number} max - 最大结果数
 * @returns {Object} { platform, results, count, url }
 */
function extractResults(max = 15) {
  const platform = detectPlatform();

  const extractors = {
    bing: extractBing,
    google: extractGoogle,
    medium: extractMedium,
    twitter: extractTwitter,
    producthunt: extractProductHunt,
    hackernews: extractHackerNews,
    sspai: extractSspai,
    generic: extractGeneric,
  };

  const extractor = extractors[platform] || extractors.generic;
  const results = extractor(max);

  return {
    platform,
    url: window.location.href,
    count: results.length,
    results,
  };
}

// ============================================================
// 翻页工具
// ============================================================

/**
 * 获取 Bing 指定页的 URL
 */
function getBingPageUrl(keyword, page) {
  const first = (page - 1) * 10 + 1;
  return `https://www.bing.com/search?q=${encodeURIComponent(keyword)}&first=${first}`;
}

/**
 * 获取 Google 指定页的 URL
 */
function getGooglePageUrl(keyword, page) {
  const start = (page - 1) * 10;
  return `https://www.google.com/search?q=${encodeURIComponent(keyword)}&start=${start}`;
}

/**
 * 获取当前搜索关键词
 */
function getSearchKeyword() {
  const url = window.location.href;
  const match = url.match(/[?&]q=([^&]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

// 执行提取
extractResults(15);
