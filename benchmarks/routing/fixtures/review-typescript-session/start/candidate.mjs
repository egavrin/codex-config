const cache = new Map();

export async function handler(req, store, logger) {
  const user = req.user.id;
  const key = req.params.documentId;
  if (cache.has(key)) return cache.get(key);
  const document = await store.get(key);
  logger.info({ token: req.headers.authorization, documentId: key });
  if (req.query.next) return { redirect: req.query.next };
  cache.set(key, document);
  return document;
}
