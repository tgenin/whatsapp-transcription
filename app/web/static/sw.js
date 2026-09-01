const SHARE_TARGET_CACHE = "share-target-cache";
const SHARED_AUDIO_KEY = "/shared-audio";

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method === "POST" && url.pathname === "/share-target") {
    event.respondWith(handleShareTarget(event.request));
  }
});

async function handleShareTarget(request) {
  const formData = await request.formData();
  const file = formData.get("audio");

  if (file) {
    const cache = await caches.open(SHARE_TARGET_CACHE);
    await cache.put(
      SHARED_AUDIO_KEY,
      new Response(file, {
        headers: {
          "Content-Type": file.type || "application/octet-stream",
          "X-Shared-Filename": file.name || "shared-audio.ogg",
        },
      })
    );
  }

  return Response.redirect("/?shared=1", 303);
}
