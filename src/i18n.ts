import { i18n } from '@nekazari/sdk';
import ca from './locales/ca.json';
import en from './locales/en.json';
import es from './locales/es.json';
import eu from './locales/eu.json';
import fr from './locales/fr.json';
import pt from './locales/pt.json';

const CONNECTIVITY_NAMESPACE = 'connectivity';

const BUNDLES: Record<string, typeof en> = { ca, en, es, eu, fr, pt };

export function registerConnectivityTranslations(): void {
  if (!i18n || typeof (i18n as any).addResourceBundle !== 'function') return;
  for (const [lang, bundle] of Object.entries(BUNDLES)) {
    i18n.addResourceBundle(lang, CONNECTIVITY_NAMESPACE, bundle, true, true);
  }
}

registerConnectivityTranslations();
