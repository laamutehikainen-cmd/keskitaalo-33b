# Keskitaalo 33B

Kaksikielinen, mobiililähtöinen vierasopas Keskitaalo 33B:lle Levillä. Sivusto on staattinen Astro-projekti ja julkaistaan GitHub Pagesissa.

## Sivuston sisältö

- Suomenkielinen mökkiopas: `/`
- English cabin guide: `/en/`
- Suomenkielinen Levi-opas: `/levi/`
- English Levi guide: `/en/levi/`

Mökkikohtaiset tekstit ovat tiedostoissa `src/content/fi/guide.yaml` ja `src/content/en/guide.yaml`. Levi-sivujen tekstit ovat vastaavissa `levi.yaml`-tiedostoissa. Sisältöskeema tarkistaa rakenteen ja varmistaa, että käännösten osiot vastaavat toisiaan.

## Paikallinen kehitys

Käytä Node.js 24:ää ja pnpm-pakettienhallintaa.

```sh
pnpm install
pnpm dev
```

Tarkistukset ja tuotantoversio:

```sh
pnpm check
pnpm build
```

## GitHub Pages

Työnkulku `.github/workflows/deploy.yml` tarkistaa, rakentaa ja julkaisee sivuston automaattisesti `main`-haaran muutoksista. GitHub-repositorion Pages-asetuksissa julkaisulähteeksi valitaan **GitHub Actions**.

Repositorion oletusnimi on `keskitaalo-33b`. `astro.config.mjs` muodostaa Pages-osoitteen GitHub Actionsin tarjoamasta omistajatiedosta ja käyttää oikeaa projektipolkua.

## Tervetulolappu

Tulosteen oikeita WiFi-tietoja ei koskaan tallenneta GitHubiin.

1. Kopioi `private/welcome-data.example.json` tiedostoksi `private/welcome-data.json`.
2. Lisää lopullinen Pages-osoite, WiFi-verkon nimi, salasana ja haluttu yhteysohje.
3. Aseta `draft` arvoon `false` vasta, kun tiedot ovat lopulliset.
4. Luo PDF:

```sh
python3 -m pip install reportlab
pnpm welcome:pdf
```

PDF ja sen vientimanifesti syntyvät paikalliseen, Gitistä ohitettuun `outputs`-kansioon. Lopullinen PDF tulee renderöidä kuvaksi ja QR-koodi testata ennen tulostamista.

## Tietosuoja ja kuvat

Julkiselle sivulle ei lisätä WiFi-tunnuksia, ovikoodeja, analytiikkaa tai henkilökohtaisia yhteystietoja. Strand Properties -vesileimallisia kuvia ei julkaista eikä niiden vesileimaa poisteta. Käyttöoikeudeltaan varmistetut kuvat voidaan lisätä myöhemmin.
