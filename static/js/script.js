document.addEventListener("DOMContentLoaded", () => {
  const locationModal = document.getElementById("locationModal");
  const mapSection = document.getElementById("mapSection");
  const profileSection = document.getElementById("profileSection");
  const allowBtn = document.getElementById("allowLocationBtn");
  const denyBtn = document.getElementById("denyLocationBtn");

  // Safety check
  if (!locationModal || !mapSection || !profileSection) {
    console.warn("Required DOM elements missing. Check your HTML structure.");
    return;
  }

  // Show modal on page load
  locationModal.classList.add("show");

  // Allow location
  allowBtn.addEventListener("click", () => getLocation());

  // Deny location
  denyBtn.addEventListener("click", () => {
    closeModal();
    showProfile();
  });

  // Retry button (externally callable)
  window.retryLocation = function () {
    profileSection.classList.add("hidden");
    mapSection.classList.add("hidden");
    locationModal.classList.add("show");
  };

  function closeModal() {
    locationModal.classList.remove("show");
  }

  function showProfile() {
    profileSection.classList.remove("hidden");
  }

  function getLocation() {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      closeModal();
      showProfile();
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        closeModal();
        showMap(position.coords.latitude, position.coords.longitude);
      },
      (error) => {
        console.error("Location error:", error);
        closeModal();
        showProfile();
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  }

  function showMap(lat, lng) {
    mapSection.classList.remove("hidden");
    profileSection.classList.add("hidden");

    const map = L.map("map").setView([lat, lng], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "© OpenStreetMap contributors",
    }).addTo(map);

    // User marker
    L.marker([lat, lng]).addTo(map).bindPopup("You're here!").openPopup();

    // 50km radius
    L.circle([lat, lng], {
      radius: 50000,
      color: "blue",
      fillColor: "#3f72af",
      fillOpacity: 0.1,
    }).addTo(map);

    fetch(`/nearby-shops?lat=${lat}&lng=${lng}`)
      .then((res) => res.json())
      .then((shops) => {
        if (!shops || shops.length === 0) {
          alert("No salons found within 50 km.");
          return;
        }

        shops.forEach((shop) => {
          const marker = L.marker([shop.lat, shop.lng]).addTo(map);
          const popupId = `popup-${shop.email.replace(/[^a-zA-Z0-9]/g, "")}`;
          marker.bindPopup(`<div id="${popupId}">Loading...</div>`);

          marker.on("popupopen", () => {
            const popupDiv = document.getElementById(popupId);
            if (popupDiv) {
              popupDiv.innerHTML = `
                <b>${shop.shop || "Unnamed Shop"}</b><br>
                Owner: ${shop.name || "Unknown"}<br>
                Distance: ${shop.distance} km<br>
                <button id="book-${popupId}">Book Now</button>
              `;

              const bookBtn = document.getElementById(`book-${popupId}`);
              bookBtn?.addEventListener("click", () =>
                bookSalon(shop.email, shop.name)
              );
            }
          });
        });
      })
      .catch((err) => {
        console.error("Error fetching shops:", err);
      });
  }

  function bookSalon(ownerEmail, ownerName) {
    const customer = JSON.parse(localStorage.getItem("customerProfile"));
    if (!customer || !customer.email || !customer.name) {
      alert("Customer details missing. Please log in or set profile.");
      return;
    }

    const data = {
      owner_email: ownerEmail,
      customer_email: customer.email,
      customer_name: customer.name,
      time: new Date().toISOString(),
      service: "Haircut",
    };

    fetch("/book-appointment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((response) => {
        if (response.status === "success") {
          alert(`Appointment booked with ${ownerName}`);
        } else {
          alert("Booking failed. Try again.");
        }
      })
      .catch((err) => {
        console.error("Booking error:", err);
        alert("Something went wrong. Try later.");
      });
  }
});
