import { i18n } from '@nekazari/sdk';
import en from './locales/en.json';
import es from './locales/es.json';

const CONNECTIVITY_NAMESPACE = 'connectivity';

export function registerConnectivityTranslations(): void {
  if (!i18n || typeof (i18n as any).addResourceBundle !== 'function') return;
  i18n.addResourceBundle('en', CONNECTIVITY_NAMESPACE, en, true, true);
  i18n.addResourceBundle('es', CONNECTIVITY_NAMESPACE, es, true, true);
}

registerConnectivityTranslations();
