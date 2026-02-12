const puppeteer = require('puppeteer');
const fs = require('fs');

console.log("🚀 O robô começou a trabalhar... aguarde o navegador abrir.");

const delay = (ms) => new Promise(res => setTimeout(res, ms));

async function handleCaptcha(page) {
    const isCaptchaVisible = await page.evaluate(() => {
        return !!document.getElementById('captcha-form') ||
            !!document.querySelector('iframe[src*="api2/anchor"]') ||
            document.body.innerText.includes("nossa rede") ||
            document.body.innerText.includes("detected unusual traffic");
    });

    if (isCaptchaVisible) {
        console.log("\n⚠️  CAPTCHA DETECTADO! Resolva-o manualmente...");
        await page.waitForFunction(() => {
            return !document.getElementById('captcha-form') &&
                !document.querySelector('iframe[src*="api2/anchor"]') &&
                !document.body.innerText.includes("detected unusual traffic");
        }, { timeout: 0 });

        console.log("✅ Captcha resolvido! Aguardando a página carregar...");
        try {
            await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 5000 });
        } catch (e) { }
        await delay(2000);
    }
}

// Função para rolar a página e carregar conteúdo dinâmico
async function autoScroll(page) {
    await page.evaluate(async () => {
        await new Promise((resolve) => {
            let totalHeight = 0;
            let distance = 100;
            let timer = setInterval(() => {
                let scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;
                if (totalHeight >= scrollHeight || totalHeight > 3000) { // Limite de 3000px para não demorar demais
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}

async function scrapeEmails() {
    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36');

    const searchTerm = 'site:instagram.com "clinica" "estetica" "botox" "beleza" "rosto" "@gmail.com"';
    await page.goto(`https://www.google.com/search?q=${encodeURIComponent(searchTerm)}`);

    let allEmails = new Set();
    const paginasParaProcessar = 10;

    for (let p = 0; p < paginasParaProcessar; p++) {
        await handleCaptcha(page);
        console.log(`\n--- Minerando Página ${p + 1} do Google ---`);

        try {
            await page.waitForSelector('h3', { timeout: 10000 });
        } catch (e) {
            await handleCaptcha(page);
        }

        const links = await page.evaluate(() => {
            const anchors = Array.from(document.querySelectorAll('a h3')).map(h3 => h3.closest('a'));
            return anchors
                .map(a => a ? a.href : null)
                .filter(href =>
                    href && href.startsWith('http') &&
                    !href.includes('google.com') &&
                    !href.includes('webcache.googleusercontent.com')
                );
        });

        console.log(`🔗 Links encontrados: ${links.length}`);

        for (let link of links) {
            const detailPage = await browser.newPage();
            try {
                // ALTERAÇÃO: Espera a rede ficar ociosa (mais chance de achar o e-mail)
                await detailPage.goto(link, { waitUntil: 'networkidle2', timeout: 25000 });

                // Rola a página para carregar conteúdos escondidos
                await autoScroll(detailPage);
                await delay(1000); // Pausa para garantir renderização final

                const textContent = await detailPage.evaluate(() => document.body.innerText);
                const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
                const found = textContent.match(emailRegex);

                if (found) {
                    found.forEach(email => {
                        const cleanEmail = email.toLowerCase();
                        if (!allEmails.has(cleanEmail)) {
                            allEmails.add(cleanEmail);
                            console.log(`  [+] Novo E-mail: ${cleanEmail}`);
                        }
                    });
                }
            } catch (err) {
                console.log(`  [!] Ignorado ou lento demais: ${link.substring(0, 30)}...`);
            } finally {
                await detailPage.close();
            }
            await delay(500); // Delay curto entre abas
        }

        fs.writeFileSync('leads_emails.txt', Array.from(allEmails).join('\n'));

        const nextButton = await page.$('#pnnext');
        if (nextButton) {
            console.log("➡️ Indo para a próxima página...");
            try {
                await Promise.all([
                    page.click('#pnnext'),
                    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 }),
                ]);
            } catch (err) {
                await handleCaptcha(page);
            }
        } else {
            await handleCaptcha(page);
            if (!(await page.$('#pnnext'))) break;
        }
    }

    console.log(`\n✅ Concluído! Total: ${allEmails.size} e-mails.`);
    await browser.close();
}

scrapeEmails().catch(err => console.error("❌ Erro fatal:", err));