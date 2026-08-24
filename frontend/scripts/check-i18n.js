#!/usr/bin/env node
/**
 * i18n-Schluessel-Check (Rework-Plan Phase C.6, docs/i18n/KONZEPT.md).
 *
 * Prueft:
 *  1. Schluessel-Paritaet: jede Datei in locales/de/ muss dieselben
 *     (verschachtelten) Schluessel haben wie ihr Gegenstueck in locales/en/
 *     und umgekehrt.
 *  2. Verwaiste Namespaces: JSON-Datei ohne erkennbare useTranslation(...)-
 *     Referenz im src-Baum (Best-Effort-Textsuche, kein vollstaendiger
 *     Scope-Resolver).
 *
 * Exit-Code 1 bei Befund, 0 wenn sauber. Gedacht fuer CI (Rework-Plan
 * Phase E) und lokale Vorab-Pruefung vor dem Commit.
 */
const fs = require('fs')
const path = require('path')

const LOCALES_DIR = path.join(__dirname, '..', 'src', 'locales')
const SRC_DIR = path.join(__dirname, '..', 'src')

function flattenKeys(obj, prefix = '') {
  let keys = []
  for (const [k, v] of Object.entries(obj)) {
    const full = prefix ? `${prefix}.${k}` : k
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      keys = keys.concat(flattenKeys(v, full))
    } else {
      keys.push(full)
    }
  }
  return keys
}

function loadNamespace(lang, ns) {
  const p = path.join(LOCALES_DIR, lang, `${ns}.json`)
  return JSON.parse(fs.readFileSync(p, 'utf-8'))
}

function listNamespaces(lang) {
  const dir = path.join(LOCALES_DIR, lang)
  return fs.readdirSync(dir).filter(f => f.endsWith('.json')).map(f => f.replace(/\.json$/, ''))
}

function walkSrc(dir, exts, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      if (entry.name === 'locales') continue
      walkSrc(full, exts, out)
    } else if (exts.some(e => entry.name.endsWith(e))) {
      out.push(full)
    }
  }
  return out
}

function main() {
  let hasError = false

  const deNs = new Set(listNamespaces('de'))
  const enNs = new Set(listNamespaces('en'))

  for (const ns of deNs) {
    if (!enNs.has(ns)) {
      console.error(`[i18n] Namespace "${ns}" existiert in de/, fehlt aber komplett in en/.`)
      hasError = true
    }
  }
  for (const ns of enNs) {
    if (!deNs.has(ns)) {
      console.error(`[i18n] Namespace "${ns}" existiert in en/, fehlt aber komplett in de/.`)
      hasError = true
    }
  }

  const commonNs = [...deNs].filter(ns => enNs.has(ns))
  for (const ns of commonNs) {
    const deKeys = new Set(flattenKeys(loadNamespace('de', ns)))
    const enKeys = new Set(flattenKeys(loadNamespace('en', ns)))

    for (const k of deKeys) {
      if (!enKeys.has(k)) {
        console.error(`[i18n] ${ns}.json: Schluessel "${k}" fehlt in en/${ns}.json.`)
        hasError = true
      }
    }
    for (const k of enKeys) {
      if (!deKeys.has(k)) {
        console.error(`[i18n] ${ns}.json: Schluessel "${k}" fehlt in de/${ns}.json.`)
        hasError = true
      }
    }
  }

  // Best-Effort: Namespaces ohne jede Erwaehnung im Quellcode (weder als
  // useTranslation('ns') noch als 'ns:' Cross-Namespace-Praefix).
  const srcFiles = walkSrc(SRC_DIR, ['.ts', '.tsx'])
  const srcContent = srcFiles.map(f => fs.readFileSync(f, 'utf-8')).join('\n')
  for (const ns of deNs) {
    const referenced = srcContent.includes(`'${ns}'`) || srcContent.includes(`"${ns}"`) || srcContent.includes(`${ns}:`)
    if (!referenced) {
      console.warn(`[i18n] Warnung: Namespace "${ns}" scheint im Quellcode nicht referenziert zu sein (verwaist?).`)
    }
  }

  if (hasError) {
    console.error('\n[i18n] Schluessel-Pruefung fehlgeschlagen.')
    process.exit(1)
  }
  console.log(`[i18n] OK - ${commonNs.length} Namespaces, Schluessel-Paritaet de/en bestaetigt.`)
}

main()
