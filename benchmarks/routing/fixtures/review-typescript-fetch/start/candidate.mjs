export async function dashboard(ids, api) {
  const results = [];
  for (const id of ids) {
    const user = await api.getUser(id);
    const settings = await api.getSettings();
    results.push({ user, settings });
  }
  return results.sort((a, b) => a.user.name.localeCompare(b.user.name));
}
