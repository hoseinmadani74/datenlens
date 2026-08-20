import { useEffect, useState, useMemo, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './App.css'

// Fix default Leaflet icon paths in Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const POPULAR_CITIES = [
  { name: 'Nuremberg', lat: 49.4521, lng: 11.0767 },
  { name: 'Berlin', lat: 52.5200, lng: 13.4050 },
  { name: 'Munich', lat: 48.1351, lng: 11.5820 },
  { name: 'Hamburg', lat: 53.5511, lng: 9.9937 },
  { name: 'Frankfurt', lat: 50.1109, lng: 8.6821 },
  { name: 'Cologne', lat: 50.9375, lng: 6.9603 },
  { name: 'Stuttgart', lat: 48.7758, lng: 9.1829 },
]

const DB_CITIES = [
  'Aachen', 'Augsburg', 'Berlin', 'Bielefeld', 'Bochum', 'Bonn', 'Braunschweig', 'Bremen',
  'Chemnitz', 'Cologne', 'Dortmund', 'Dresden', 'Duisburg', 'Düsseldorf', 'Erfurt', 'Essen',
  'Frankfurt am Main', 'Freiburg im Breisgau', 'Gelsenkirchen', 'Halle (Saale)', 'Hamburg',
  'Hanover', 'Karlsruhe', 'Kassel', 'Kiel', 'Krefeld', 'Leipzig', 'Lübeck', 'Magdeburg',
  'Mainz', 'Mannheim', 'Mönchengladbach', 'Munich', 'Münster', 'Nuremberg', 'Oberhausen',
  'Rostock', 'Stuttgart', 'Wiesbaden', 'Wuppertal',
]

const WEATHER_OPTIONS = [
  { id: 'clear', label: 'Clear / Dry', icon: '☀️', desc: 'Optimal rail conditions' },
  { id: 'rain', label: 'Moderate Rain', icon: '🌧️', desc: 'Wet rails (+20% risk)' },
  { id: 'heavy_rain', label: 'Heavy Rain / Storm', icon: '⛈️', desc: 'Flooding risk (+45% risk)' },
  { id: 'snow_ice', label: 'Snow & Catenary Ice', icon: '❄️', desc: 'Switch icing (+68% risk)' },
  { id: 'high_wind', label: 'High Wind (>60 km/h)', icon: '💨', desc: 'Speed limits (+78% risk)' },
  { id: 'extreme_heat', label: 'Extreme Heat (>32°C)', icon: '🌡️', desc: 'Rail expansion (+25% risk)' },
]

const ROUTE_PRESETS = [
  { origin: 'Frankfurt am Main', destination: 'Cologne', label: 'Frankfurt ➔ Köln' },
  { origin: 'Berlin', destination: 'Munich', label: 'Berlin ➔ München' },
  { origin: 'Hamburg', destination: 'Cologne', label: 'Hamburg ➔ Köln' },
  { origin: 'Stuttgart', destination: 'Frankfurt am Main', label: 'Stuttgart ➔ Frankfurt' },
  { origin: 'Dortmund', destination: 'Düsseldorf', label: 'Dortmund ➔ Düsseldorf' },
  { origin: 'Nuremberg', destination: 'Munich', label: 'Nürnberg ➔ München' },
]

const ROUTE_MAP = {
  fuel: {
    path: '/fuel_price',
    aliases: ['/', '/fuel', '/fuel_price', '/fuel-price', '/gas', '/fuel_price/'],
    title: 'Datenlens | Live Fuel Prices & Gas Stations Germany',
  },
  trains: {
    path: '/trains',
    aliases: ['/trains', '/train-delays', '/db-delays', '/delays', '/trains/'],
    title: 'Datenlens | Deutsche Bahn Delay Intelligence & Forecaster',
  },
  housing: {
    path: '/housing',
    aliases: ['/housing', '/rent', '/mietspiegel', '/housing-market', '/housing/'],
    title: 'Datenlens | Germany Housing & Rental Index',
  },
  jobs: {
    path: '/jobs',
    aliases: ['/jobs', '/tech-jobs', '/jobs-radar', '/career', '/jobs/'],
    title: 'Datenlens | Tech Jobs Radar Germany (English-Friendly)',
  },
  dashboard: {
    path: '/energy',
    aliases: ['/energy', '/markets', '/dashboard', '/oil', '/energy/'],
    title: 'Datenlens | Energy Markets & Commodity Analytics',
  },
  portfolio: {
    path: '/aboutus',
    aliases: ['/aboutus', '/about-us', '/about', '/portfolio', '/resume', '/aboutus/'],
    title: 'Datenlens | About Us & Engineering Portfolio',
  },
}

function resolveTabFromPath(path) {
  const normalized = (path || '/').toLowerCase().replace(/\/$/, '') || '/'
  for (const [key, config] of Object.entries(ROUTE_MAP)) {
    if (config.aliases.some((a) => (a === '/' ? normalized === '/' : a.replace(/\/$/, '') === normalized))) {
      return key
    }
  }
  return 'fuel'
}

export default function App() {
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined') {
      return resolveTabFromPath(window.location.pathname)
    }
    return 'fuel'
  })
  const [stations, setStations] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [oilData, setOilData] = useState([])
  const [housingData, setHousingData] = useState(null)
  const [dbData, setDbData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isCached, setIsCached] = useState(false)

  // Tech Jobs Radar state
  const [jobs, setJobs] = useState([])
  const [jobsLoading, setJobsLoading] = useState(false)
  const [selectedHours, setSelectedHours] = useState(24)
  const [searchKeyword, setSearchKeyword] = useState('Data Analyst')
  const [jobsError, setJobsError] = useState(null)

  // Search & Location state (Fuel)
  const [locationName, setLocationName] = useState('Nuremberg')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searchingCity, setSearchingCity] = useState(false)
  const [isLocating, setIsLocating] = useState(false)
  const [lat, setLat] = useState(49.4521)
  const [lng, setLng] = useState(11.0767)
  const [rad, setRad] = useState(5.0)

  // Fuel Filter, Sort & Map Selection state
  const [sortBy, setSortBy] = useState('dist') // 'dist' | 'e5' | 'diesel' | 'e10'
  const [openOnly, setOpenOnly] = useState(false)
  const [selectedStationId, setSelectedStationId] = useState(null)

  // DB Train state
  const [dbSearch, setDbSearch] = useState('')
  const [dbStateFilter, setDbStateFilter] = useState('All')
  const [dbSort, setDbSort] = useState('punctuality') // 'punctuality' | 'worst' | 'delay' | 'trains'

  // DB Route Delay Forecaster state
  const [originCity, setOriginCity] = useState('Frankfurt am Main')
  const [destCity, setDestCity] = useState('Cologne')
  const [selectedWeather, setSelectedWeather] = useState('clear')
  const [departureHour, setDepartureHour] = useState(17)
  const [dayType, setDayType] = useState('weekday')
  const [forecastData, setForecastData] = useState(null)
  const [forecastLoading, setForecastLoading] = useState(false)
  const [forecastError, setForecastError] = useState(null)

  // Housing Calculator state
  const [calcCityId, setCalcCityId] = useState('muc')
  const [calcSize, setCalcSize] = useState(65)
  const [housingRegion, setHousingRegion] = useState('All')
  const [housingSort, setHousingSort] = useState('kaltmiete')

  // Leaflet map refs
  const mapContainerRef = useRef(null)
  const mapInstanceRef = useRef(null)
  const markersGroupRef = useRef(null)
  const circleLayerRef = useRef(null)
  const centerMarkerRef = useRef(null)

  // URL Navigation helper
  const navigateTo = (tabKey, push = true) => {
    setActiveTab(tabKey)
    const config = ROUTE_MAP[tabKey]
    if (config) {
      document.title = config.title
      if (push && typeof window !== 'undefined' && window.location.pathname !== config.path) {
        window.history.pushState({ tab: tabKey }, '', config.path)
      }
    }
  }

  // Fetch Live Gas Station Data
  const fetchGasStations = (targetLat = lat, targetLng = lng, targetRad = rad) => {
    setLoading(true)
    setError(null)
    fetch(`/api/gas-stations?lat=${targetLat}&lng=${targetLng}&rad=${targetRad}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP Error ${res.status}: Failed to reach API`)
        return res.json()
      })
      .then((data) => {
        if (data.success) {
          setStations(data.stations || [])
          setAnalytics(data.analytics || null)
          setIsCached(Boolean(data.cached))
        } else {
          setError(data.message || 'Error loading fuel data')
        }
        setLoading(false)
      })
      .catch((err) => {
        console.error('Fetch error:', err)
        setError(err.message)
        setLoading(false)
      })
  }

  // Handle City / Address Search Geocoding
  const handleCitySearch = (e) => {
    if (e) e.preventDefault()
    if (!searchQuery.trim() || searchQuery.trim().length < 2) return

    setSearchingCity(true)
    fetch(`/api/geocode?q=${encodeURIComponent(searchQuery.trim())}`)
      .then((res) => res.json())
      .then((data) => {
        setSearchingCity(false)
        if (data.success && data.results && data.results.length > 0) {
          setSearchResults(data.results)
          if (data.results.length === 1) {
            selectLocation(data.results[0])
          }
        } else {
          setSearchResults([])
          setError(`No locations found in Germany for "${searchQuery}".`)
        }
      })
      .catch((err) => {
        setSearchingCity(false)
        console.error('Geocode error:', err)
      })
  }

  // Select Location from Search or Preset
  const selectLocation = (loc) => {
    const newLat = parseFloat(loc.lat)
    const newLng = parseFloat(loc.lng)
    const newName = loc.name || loc.display_name?.split(',')[0] || 'Selected Location'

    setLocationName(newName)
    setLat(newLat)
    setLng(newLng)
    setSearchResults([])
    setSearchQuery('')
    fetchGasStations(newLat, newLng, rad)

    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([newLat, newLng], getZoomLevel(rad), { duration: 1.2 })
    }
  }

  // Detect Client GPS Location via Browser Geolocation API
  const handleDetectLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser.')
      return
    }

    setIsLocating(true)
    setError(null)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setIsLocating(false)
        const userLat = pos.coords.latitude
        const userLng = pos.coords.longitude
        setLocationName('Your Current Location')
        setLat(userLat)
        setLng(userLng)
        fetchGasStations(userLat, userLng, rad)

        if (mapInstanceRef.current) {
          mapInstanceRef.current.flyTo([userLat, userLng], getZoomLevel(rad), { duration: 1.2 })
        }
      },
      (err) => {
        setIsLocating(false)
        console.warn('Geolocation error:', err)
        setError('Could not retrieve your location. Please check browser permissions or search for your city.')
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }

  // Helper for map zoom based on radius
  const getZoomLevel = (radiusKm) => {
    if (radiusKm <= 3) return 14
    if (radiusKm <= 7) return 13
    if (radiusKm <= 15) return 12
    return 11
  }

  // Handle Radius Change
  const handleRadiusChange = (newRad) => {
    const radiusVal = parseFloat(newRad)
    setRad(radiusVal)
    fetchGasStations(lat, lng, radiusVal)
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setZoom(getZoomLevel(radiusVal))
    }
  }

  // Fetch Tech Jobs Radar Listings
  const fetchJobs = (keyword = searchKeyword, hours = selectedHours) => {
    setJobsLoading(true)
    setJobsError(null)
    fetch(`/api/jobs?query=${encodeURIComponent(keyword)}&hours=${hours}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP Error ${res.status}: Failed to reach Jobs API`)
        return res.json()
      })
      .then((data) => {
        if (data.success) {
          setJobs(data.jobs || [])
        } else {
          setJobsError(data.message || 'Error fetching tech jobs')
        }
        setJobsLoading(false)
      })
      .catch((err) => {
        console.error('Job fetch error:', err)
        setJobsError(err.message)
        setJobsLoading(false)
      })
  }

  // Fetch DB Corridor Delay Forecast
  const fetchDelayForecast = (
    orig = originCity,
    dest = destCity,
    w = selectedWeather,
    h = departureHour,
    dt = dayType
  ) => {
    setForecastLoading(true)
    setForecastError(null)
    const url = `/api/train-delay-forecast?origin=${encodeURIComponent(orig)}&destination=${encodeURIComponent(dest)}&weather=${w}&hour=${h}&day_type=${dt}`
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP Error ${res.status}: Failed to fetch train forecast`)
        return res.json()
      })
      .then((data) => {
        if (data.success) {
          setForecastData(data)
        } else {
          setForecastError(data.message || 'Forecast computation failed')
        }
        setForecastLoading(false)
      })
      .catch((err) => {
        console.error('Forecast fetch error:', err)
        setForecastError(err.message)
        setForecastLoading(false)
      })
  }

  // Live recalculate DB Delay Forecast on parameter change
  useEffect(() => {
    fetchDelayForecast(originCity, destCity, selectedWeather, departureHour, dayType)
  }, [originCity, destCity, selectedWeather, departureHour, dayType])

  // Initial Data Load & PopState History Listener
  useEffect(() => {
    const initialTab = resolveTabFromPath(window.location.pathname)
    setActiveTab(initialTab)
    if (ROUTE_MAP[initialTab]) {
      document.title = ROUTE_MAP[initialTab].title
    }

    const handlePopState = () => {
      const currentTab = resolveTabFromPath(window.location.pathname)
      setActiveTab(currentTab)
      if (ROUTE_MAP[currentTab]) {
        document.title = ROUTE_MAP[currentTab].title
      }
    }

    window.addEventListener('popstate', handlePopState)

    fetch('/api/oil-data')
      .then((res) => res.json())
      .then((data) => setOilData(data))
      .catch((err) => console.error('Oil fetch error:', err))

    fetch('/api/housing-data')
      .then((res) => res.json())
      .then((data) => setHousingData(data))
      .catch((err) => console.error('Housing fetch error:', err))

    fetch('/api/db-punctuality')
      .then((res) => res.json())
      .then((data) => setDbData(data))
      .catch((err) => console.error('DB fetch error:', err))

    fetchGasStations(lat, lng, rad)
    fetchJobs('Data Analyst', 24)

    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  // Initialize Leaflet Map
  useEffect(() => {
    if (activeTab !== 'fuel') return

    if (!mapInstanceRef.current && mapContainerRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [lat, lng],
        zoom: getZoomLevel(rad),
        zoomControl: true,
      })

      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
      }).addTo(map)

      map.on('click', (e) => {
        const clickedLat = e.latlng.lat
        const clickedLng = e.latlng.lng
        setLocationName('Custom Map Point')
        setLat(clickedLat)
        setLng(clickedLng)
        fetchGasStations(clickedLat, clickedLng, rad)
      })

      markersGroupRef.current = L.layerGroup().addTo(map)
      mapInstanceRef.current = map
    }
  }, [activeTab])

  // Update Center Marker & Radius Circle on Map
  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map) return

    if (centerMarkerRef.current) {
      centerMarkerRef.current.setLatLng([lat, lng])
    } else {
      const centerIcon = L.divIcon({
        className: 'custom-center-marker',
        html: `<div class="center-pulse-pin"><span class="pulse-ring"></span><span class="pin-dot"></span></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      })
      centerMarkerRef.current = L.marker([lat, lng], { icon: centerIcon, zIndexOffset: 1000 }).addTo(map)
      centerMarkerRef.current.bindPopup(`<b>Search Center:</b><br/>${locationName}`)
    }

    if (circleLayerRef.current) {
      circleLayerRef.current.setLatLng([lat, lng])
      circleLayerRef.current.setRadius(rad * 1000)
    } else {
      circleLayerRef.current = L.circle([lat, lng], {
        radius: rad * 1000,
        color: '#0284c7',
        fillColor: '#38bdf8',
        fillOpacity: 0.12,
        weight: 2,
        dashArray: '4, 6',
      }).addTo(map)
    }
  }, [lat, lng, rad, locationName])

  // Update Station Markers on Map
  useEffect(() => {
    const map = mapInstanceRef.current
    const markersGroup = markersGroupRef.current
    if (!map || !markersGroup) return

    markersGroup.clearLayers()

    stations.forEach((s) => {
      if (!s.lat || !s.lng) return

      const isMinE5 = analytics?.min_e5 && s.e5 === analytics.min_e5
      const isMinDiesel = analytics?.min_diesel && s.diesel === analytics.min_diesel
      const isSelected = selectedStationId === s.id

      const markerClass = `station-marker-pin ${s.isOpen ? 'open' : 'closed'} ${
        isMinE5 || isMinDiesel ? 'cheapest' : ''
      } ${isSelected ? 'selected' : ''}`

      const displayPrice = s.e5 ? `${s.e5}€` : s.diesel ? `${s.diesel}€` : (s.isOpen ? 'Open' : 'Off')

      const customIcon = L.divIcon({
        className: 'custom-station-icon',
        html: `
          <div class="${markerClass}">
            <span class="marker-price">${displayPrice}</span>
            ${isMinE5 || isMinDiesel ? '<span class="star-badge">★</span>' : ''}
          </div>
        `,
        iconSize: [44, 28],
        iconAnchor: [22, 28],
      })

      const marker = L.marker([s.lat, s.lng], { icon: customIcon })

      const popupContent = `
        <div class="map-popup-card">
          <div class="popup-header">
            <h4>${s.brand || s.name}</h4>
            <span class="popup-badge ${s.isOpen ? 'open' : 'closed'}">${s.isOpen ? 'Open' : 'Closed'}</span>
          </div>
          <p class="popup-address">📍 ${s.street} ${s.houseNumber || ''}, ${s.postCode} ${s.place} (${s.dist} km)</p>
          <div class="popup-prices">
            <div class="p-item ${isMinDiesel ? 'highlight' : ''}">
              <span>Diesel</span><strong>${s.diesel ? `${s.diesel} €` : '-'}</strong>
            </div>
            <div class="p-item ${isMinE5 ? 'highlight' : ''}">
              <span>Super E5</span><strong>${s.e5 ? `${s.e5} €` : '-'}</strong>
            </div>
            <div class="p-item">
              <span>Super E10</span><strong>${s.e10 ? `${s.e10} €` : '-'}</strong>
            </div>
          </div>
          <a href="https://www.google.com/maps/dir/?api=1&destination=${s.lat},${s.lng}" target="_blank" rel="noopener noreferrer" class="popup-nav-link">
            Directions via Google Maps ↗
          </a>
        </div>
      `

      marker.bindPopup(popupContent)
      marker.on('click', () => setSelectedStationId(s.id))
      markersGroup.addLayer(marker)
    })
  }, [stations, analytics, selectedStationId])

  // Focus station on map from card click
  const handleFocusStation = (station) => {
    setSelectedStationId(station.id)
    if (mapInstanceRef.current && station.lat && station.lng) {
      mapInstanceRef.current.flyTo([station.lat, station.lng], 15, { duration: 0.8 })
    }
  }

  // Processed / Sorted Fuel Stations
  const processedStations = useMemo(() => {
    let list = [...stations]
    if (openOnly) {
      list = list.filter((s) => s.isOpen)
    }

    list.sort((a, b) => {
      if (sortBy === 'dist') return (a.dist || 0) - (b.dist || 0)
      if (sortBy === 'e5') return (a.e5 || 999) - (b.e5 || 999)
      if (sortBy === 'diesel') return (a.diesel || 999) - (b.diesel || 999)
      if (sortBy === 'e10') return (a.e10 || 999) - (b.e10 || 999)
      return 0
    })

    return list
  }, [stations, openOnly, sortBy])

  // Processed DB Stations (Filtered & Sorted)
  const processedDbStations = useMemo(() => {
    if (!dbData?.all_stations) return []
    let list = [...dbData.all_stations]

    if (dbSearch.trim()) {
      const q = dbSearch.toLowerCase().trim()
      list = list.filter(
        (s) =>
          s.city.toLowerCase().includes(q) ||
          s.station.toLowerCase().includes(q) ||
          s.state.toLowerCase().includes(q)
      )
    }

    if (dbStateFilter !== 'All') {
      list = list.filter((s) => s.state === dbStateFilter)
    }

    list.sort((a, b) => {
      if (dbSort === 'punctuality') return b.punctuality_pct - a.punctuality_pct
      if (dbSort === 'worst') return a.punctuality_pct - b.punctuality_pct
      if (dbSort === 'delay') return b.avg_delay_minutes - a.avg_delay_minutes
      if (dbSort === 'trains') return b.daily_trains - a.daily_trains
      return 0
    })

    return list
  }, [dbData, dbSearch, dbStateFilter, dbSort])

  // DB States List
  const dbStatesList = useMemo(() => {
    if (!dbData?.all_stations) return ['All']
    const states = Array.from(new Set(dbData.all_stations.map((s) => s.state))).sort()
    return ['All', ...states]
  }, [dbData])

  // Processed / Filtered Housing Cities
  const processedHousingCities = useMemo(() => {
    if (!housingData?.cities) return []
    let list = [...housingData.cities]
    if (housingRegion !== 'All') {
      list = list.filter((c) => c.region === housingRegion)
    }
    list.sort((a, b) => {
      if (housingSort === 'kaltmiete') return b.kaltmiete - a.kaltmiete
      if (housingSort === 'warmmiete') return b.warmmiete - a.warmmiete
      if (housingSort === 'growth') return b.yoy_growth - a.yoy_growth
      if (housingSort === 'burden') return b.rent_burden_pct - a.rent_burden_pct
      return 0
    })
    return list
  }, [housingData, housingRegion, housingSort])

  // Active City for Rent Calculator
  const activeCalcCity = useMemo(() => {
    if (!housingData?.cities) return null
    return housingData.cities.find((c) => c.id === calcCityId) || housingData.cities[0]
  }, [housingData, calcCityId])

  const calculatedRent = useMemo(() => {
    if (!activeCalcCity) return { kalt: 0, neben: 0, warm: 0, minIncome: 0 }
    const kalt = Math.round(activeCalcCity.kaltmiete * calcSize)
    const neben = Math.round(activeCalcCity.nebenkosten_m2 * calcSize)
    const warm = kalt + neben
    const minIncome = Math.round(warm / 0.3)
    return { kalt, neben, warm, minIncome }
  }, [activeCalcCity, calcSize])

  const latestOil = oilData.length > 0 ? oilData[oilData.length - 1] : null

  return (
    <div className="app-container">
      {/* Navigation Header */}
      <header className="navbar">
        <div className="brand" onClick={() => navigateTo('fuel')}>
          <span className="logo-accent">Daten</span>lens
          <span className="badge">GERMANY</span>
        </div>
        <nav className="nav-links">
          <button
            className={`nav-btn ${activeTab === 'fuel' ? 'active' : ''}`}
            onClick={() => navigateTo('fuel')}
          >
            ⛽ Fuel Map
          </button>
          <button
            className={`nav-btn ${activeTab === 'trains' ? 'active' : ''}`}
            onClick={() => navigateTo('trains')}
          >
            🚆 DB Delays & Forecaster
          </button>
          <button
            className={`nav-btn ${activeTab === 'housing' ? 'active' : ''}`}
            onClick={() => navigateTo('housing')}
          >
            🏢 Housing & Rent
          </button>
          <button
            className={`nav-btn ${activeTab === 'jobs' ? 'active' : ''}`}
            onClick={() => navigateTo('jobs')}
          >
            🎯 Tech Jobs Radar
          </button>
          <button
            className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => navigateTo('dashboard')}
          >
            📈 Energy Markets
          </button>
          <button
            className={`nav-btn ${activeTab === 'portfolio' ? 'active' : ''}`}
            onClick={() => navigateTo('portfolio')}
          >
            👤 Portfolio & Resume
          </button>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="content">
        {/* ========================================================
            TAB 1: LIVE FUEL MAP & MONITOR
        ======================================================== */}
        {activeTab === 'fuel' && (
          <div className="fuel-container">
            <div className="section-header">
              <div className="header-badge-row">
                <span className="api-badge">MTS-K Official Data</span>
                <span className="ssl-badge">🔒 HTTPS Secure</span>
                {isCached && <span className="cache-badge">⚡ Cached (5m TTL)</span>}
              </div>
              <h2>Germany Real-time Fuel Price Monitor & Interactive Map</h2>
              <p>Search any German city or detect your live location to view stations and compare prices within your radius.</p>
            </div>

            {/* Top Search & Control Section */}
            <div className="map-search-panel">
              <form className="city-search-form" onSubmit={handleCitySearch}>
                <div className="search-input-wrapper">
                  <span className="search-icon">🔍</span>
                  <input
                    type="text"
                    placeholder="Search city, town, or postal code in Germany (e.g. Erlangen, Berlin, München)..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value)
                      if (e.target.value.length >= 3) {
                        handleCitySearch()
                      }
                    }}
                  />
                  {searchQuery && (
                    <button type="button" className="clear-btn" onClick={() => { setSearchQuery(''); setSearchResults([]); }}>
                      ✕
                    </button>
                  )}
                </div>
                <button type="submit" className="search-action-btn" disabled={searchingCity}>
                  {searchingCity ? 'Searching...' : 'Search'}
                </button>
                <button
                  type="button"
                  className="detect-location-btn"
                  onClick={handleDetectLocation}
                  disabled={isLocating}
                  title="Detect your current location using GPS"
                >
                  {isLocating ? '📍 Locating...' : '📍 Detect My Location'}
                </button>
              </form>

              {/* Autocomplete Search Results Dropdown */}
              {searchResults.length > 0 && (
                <div className="search-dropdown-menu">
                  {searchResults.map((res, i) => (
                    <div key={i} className="dropdown-item" onClick={() => selectLocation(res)}>
                      <span className="dropdown-name">{res.name}</span>
                      <span className="dropdown-full">{res.display_name}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Quick City Presets */}
              <div className="city-pills-row">
                <span className="pills-label">Popular Cities:</span>
                {POPULAR_CITIES.map((c) => (
                  <button
                    key={c.name}
                    className={`city-pill ${locationName === c.name ? 'active' : ''}`}
                    onClick={() => selectLocation(c)}
                  >
                    {c.name}
                  </button>
                ))}
              </div>

              {/* Radius Selector Slider & Presets */}
              <div className="radius-control-bar">
                <div className="radius-label-wrap">
                  <span className="radius-title">Search Radius:</span>
                  <span className="radius-val-highlight">{rad} km</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="25"
                  step="0.5"
                  value={rad}
                  onChange={(e) => handleRadiusChange(e.target.value)}
                  className="radius-slider"
                />
                <div className="radius-preset-buttons">
                  {[2, 5, 10, 15, 25].map((r) => (
                    <button
                      key={r}
                      className={`rad-btn ${rad === r ? 'active' : ''}`}
                      onClick={() => handleRadiusChange(r)}
                    >
                      {r} km
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Analytics Summary Bar */}
            {analytics && !loading && (
              <div className="analytics-summary-bar">
                <div className="summary-stat">
                  <span className="stat-label">Area: {locationName}</span>
                  <span className="stat-value">{analytics.total_stations} Stations ({analytics.open_stations} Open)</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Avg Super E5</span>
                  <span className="stat-value text-cyan">{analytics.avg_e5 ? `${analytics.avg_e5} €` : '-'}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Lowest E5</span>
                  <span className="stat-value text-emerald">{analytics.min_e5 ? `${analytics.min_e5} €` : '-'}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Avg Diesel</span>
                  <span className="stat-value text-cyan">{analytics.avg_diesel ? `${analytics.avg_diesel} €` : '-'}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Lowest Diesel</span>
                  <span className="stat-value text-emerald">{analytics.min_diesel ? `${analytics.min_diesel} €` : '-'}</span>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && <div className="error-msg">⚠️ {error}</div>}

            {/* Split View: Left List / Right Interactive Map */}
            <div className="map-content-split">
              <div className="stations-column">
                <div className="filter-toolbar">
                  <div className="filter-group">
                    <label>Sort By:</label>
                    <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                      <option value="dist">Distance (Closest)</option>
                      <option value="e5">Super E5 (Cheapest)</option>
                      <option value="diesel">Diesel (Cheapest)</option>
                      <option value="e10">Super E10 (Cheapest)</option>
                    </select>
                  </div>

                  <div className="filter-group-checkbox">
                    <label>
                      <input
                        type="checkbox"
                        checked={openOnly}
                        onChange={(e) => setOpenOnly(e.target.checked)}
                      />
                      <span>Open Only</span>
                    </label>
                  </div>
                </div>

                {loading && <div className="status-msg">Fetching live station data from Tankerkönig API...</div>}

                {!loading && processedStations.length === 0 && (
                  <div className="no-data">
                    No gas stations found within {rad} km of {locationName}. Try increasing the radius slider.
                  </div>
                )}

                <div className="stations-scroll-list">
                  {processedStations.map((s) => {
                    const isMinE5 = analytics?.min_e5 && s.e5 === analytics.min_e5
                    const isMinDiesel = analytics?.min_diesel && s.diesel === analytics.min_diesel
                    const isSelected = selectedStationId === s.id

                    return (
                      <div
                        key={s.id}
                        className={`station-card ${s.isOpen ? 'open' : 'closed'} ${
                          isSelected ? 'active-selection' : ''
                        }`}
                        onClick={() => handleFocusStation(s)}
                      >
                        <div className="station-card-header">
                          <div>
                            <h4>{s.brand || s.name}</h4>
                            <span className="station-subtitle">{s.name}</span>
                          </div>
                          <span className={`status-badge ${s.isOpen ? 'open' : 'closed'}`}>
                            {s.isOpen ? 'Open' : 'Closed'}
                          </span>
                        </div>

                        <p className="station-address">
                          📍 {s.street} {s.houseNumber || ''}, {s.postCode} {s.place}
                          <span className="distance-tag">({s.dist} km)</span>
                        </p>

                        <div className="price-box-grid">
                          <div className={`price-item ${isMinDiesel ? 'highlight-cheapest' : ''}`}>
                            <span className="fuel-type">
                              Diesel {isMinDiesel && <span className="mini-badge">Cheapest</span>}
                            </span>
                            <span className="fuel-price">{s.diesel ? `${s.diesel} €` : '-'}</span>
                          </div>
                          <div className={`price-item ${isMinE5 ? 'highlight-cheapest' : ''}`}>
                            <span className="fuel-type">
                              Super E5 {isMinE5 && <span className="mini-badge">Cheapest</span>}
                            </span>
                            <span className="fuel-price">{s.e5 ? `${s.e5} €` : '-'}</span>
                          </div>
                          <div className="price-item">
                            <span className="fuel-type">Super E10</span>
                            <span className="fuel-price">{s.e10 ? `${s.e10} €` : '-'}</span>
                          </div>
                        </div>

                        <div className="card-action-row">
                          <span className="map-view-hint">🎯 Focus on Map</span>
                          <a
                            href={`https://www.google.com/maps/dir/?api=1&destination=${s.lat},${s.lng}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="card-maps-link"
                            onClick={(e) => e.stopPropagation()}
                          >
                            Directions ↗
                          </a>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Right Column: Interactive Leaflet Map */}
              <div className="map-column">
                <div className="map-wrapper-card">
                  <div className="map-header-info">
                    <span className="map-instruction">💡 Click anywhere on the map to set a new search point</span>
                    <span className="map-count-tag">{stations.length} Pins</span>
                  </div>
                  <div id="fuel-map" ref={mapContainerRef} className="leaflet-map-container" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================
            TAB 2: DEUTSCHE BAHN (DB) PUNCTUALITY & DELAYS
        ======================================================== */}
        {activeTab === 'trains' && (
          <div className="trains-container">
            <div className="section-header">
              <div className="header-badge-row">
                <span className="api-badge">Federal Railway Intelligence</span>
                <span className="ssl-badge">Cities &gt; 200,000 Pop</span>
                <span className="cache-badge">2h Cancellation Penalty Applied</span>
              </div>
              <h2>Deutsche Bahn (DB) Punctuality & Delay Intelligence</h2>
              <p>
                Comprehensive punctuality ranking and delay distribution across major German rail hubs in cities with over 200,000 inhabitants. Punctual is defined as delay &lt; 5 min. Cancellations are weighted as a 2-hour (120 min) delay penalty.
              </p>
            </div>

            {/* DB Summary KPIs */}
            {dbData && (
              <div className="housing-kpi-grid">
                <div className="kpi-card">
                  <span className="kpi-label">National Avg Punctuality</span>
                  <span className="kpi-value text-cyan">{dbData.summary.national_avg_punctuality}%</span>
                  <span className="kpi-sub">On-time (Delay &lt; 5 min)</span>
                </div>
                <div className="kpi-card">
                  <span className="kpi-label">Average Delay / Train</span>
                  <span className="kpi-value text-emerald">{dbData.summary.national_avg_delay_minutes} min</span>
                  <span className="kpi-sub">Incl. 120m cancellation penalty</span>
                </div>
                <div className="kpi-card">
                  <span className="kpi-label">🏆 Top Punctual Station</span>
                  <span className="kpi-value text-emerald">{dbData.summary.best_station.punctuality}%</span>
                  <span className="kpi-sub">{dbData.summary.best_station.name}</span>
                </div>
                <div className="kpi-card">
                  <span className="kpi-label">⚠️ Most Delayed Station</span>
                  <span className="kpi-value text-rose">{dbData.summary.worst_station.punctuality}%</span>
                  <span className="kpi-sub">{dbData.summary.worst_station.name}</span>
                </div>
              </div>
            )}

            {/* ========================================================
                DB CORRIDOR ROUTE DELAY PROBABILITY FORECASTER
            ======================================================== */}
            <div className="db-forecaster-card">
              <div className="forecaster-header">
                <div className="header-badge-row">
                  <span className="api-badge">Predictive AI Model</span>
                  <span className="ssl-badge">Weather & Corridors</span>
                  <span className="cache-badge">40 Hub Network</span>
                </div>
                <h3>🚆 DB Corridor Route Delay Risk & Weather Forecaster</h3>
                <p>
                  Simulate and forecast departure delay probability, expected waiting time, and junction congestion using our multi-variable model combining weather stress, peak commuter windows, and network bottleneck scores.
                </p>
              </div>

              {/* Quick Route Presets */}
              <div className="route-presets-bar">
                <span className="preset-label">Popular Routes:</span>
                <div className="preset-chips">
                  {ROUTE_PRESETS.map((p) => (
                    <button
                      key={p.label}
                      type="button"
                      className={`preset-chip ${originCity === p.origin && destCity === p.destination ? 'active' : ''}`}
                      onClick={() => {
                        setOriginCity(p.origin)
                        setDestCity(p.destination)
                      }}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="forecaster-main-grid">
                {/* Left Column: Interactive Simulation Controls */}
                <div className="forecaster-controls-panel">
                  {/* Route Selectors */}
                  <div className="fc-control-group">
                    <label className="fc-label">Select Origin & Destination</label>
                    <div className="route-select-row">
                      <div className="select-col">
                        <span className="col-sub">Departure (Origin)</span>
                        <select
                          className="fc-select"
                          value={originCity}
                          onChange={(e) => setOriginCity(e.target.value)}
                        >
                          {DB_CITIES.map((c) => (
                            <option key={c} value={c} disabled={c === destCity}>
                              {c}
                            </option>
                          ))}
                        </select>
                      </div>

                      <button
                        type="button"
                        className="swap-route-btn"
                        title="Swap Origin and Destination"
                        onClick={() => {
                          const temp = originCity
                          setOriginCity(destCity)
                          setDestCity(temp)
                        }}
                      >
                        ⇄
                      </button>

                      <div className="select-col">
                        <span className="col-sub">Arrival (Destination)</span>
                        <select
                          className="fc-select"
                          value={destCity}
                          onChange={(e) => setDestCity(e.target.value)}
                        >
                          {DB_CITIES.map((c) => (
                            <option key={c} value={c} disabled={c === originCity}>
                              {c}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Weather Conditions */}
                  <div className="fc-control-group">
                    <label className="fc-label">Weather & Atmospheric Conditions</label>
                    <div className="weather-btn-grid">
                      {WEATHER_OPTIONS.map((w) => (
                        <button
                          key={w.id}
                          type="button"
                          className={`weather-btn ${selectedWeather === w.id ? 'active' : ''}`}
                          onClick={() => setSelectedWeather(w.id)}
                        >
                          <span className="w-icon">{w.icon}</span>
                          <div className="w-text">
                            <span className="w-title">{w.label}</span>
                            <span className="w-desc">{w.desc}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Time of Day & Rush Hour Slider */}
                  <div className="fc-control-group">
                    <div className="fc-label-row">
                      <label className="fc-label">Departure Time Window</label>
                      <span className="time-display-badge">
                        🕒 {String(departureHour).padStart(2, '0')}:00 Uhr
                        {((departureHour >= 6 && departureHour <= 9) || (departureHour >= 15 && departureHour <= 19)) && (
                          <span className="rush-indicator"> • Rush Hour Peak</span>
                        )}
                      </span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="23"
                      value={departureHour}
                      onChange={(e) => setDepartureHour(Number(e.target.value))}
                      className="fc-slider"
                    />
                    <div className="slider-ticks">
                      <span>00:00 (Night)</span>
                      <span className="tick-peak">08:00 (Morning Peak)</span>
                      <span>12:00</span>
                      <span className="tick-peak">17:00 (Evening Peak)</span>
                      <span>23:00</span>
                    </div>
                  </div>

                  {/* Day Type Toggle */}
                  <div className="fc-control-group">
                    <label className="fc-label">Day of Travel</label>
                    <div className="day-type-segmented">
                      <button
                        type="button"
                        className={`day-btn ${dayType === 'weekday' ? 'active' : ''}`}
                        onClick={() => setDayType('weekday')}
                      >
                        🏢 Regular Weekday (Mon - Fri)
                      </button>
                      <button
                        type="button"
                        className={`day-btn ${dayType === 'weekend' ? 'active' : ''}`}
                        onClick={() => setDayType('weekend')}
                      >
                        🎉 Weekend / Holiday (+12% Load)
                      </button>
                    </div>
                  </div>
                </div>

                {/* Right Column: Live Risk Output */}
                <div className="forecaster-results-panel">
                  {forecastLoading ? (
                    <div className="fc-loading-box">
                      <div className="spinner"></div>
                      <span>Computing corridor congestion & weather coefficients...</span>
                    </div>
                  ) : forecastData ? (
                    <div className="fc-result-card">
                      {/* Top Score Banner */}
                      <div className="fc-score-header">
                        <div>
                          <span className="fc-route-headline">
                            {forecastData.route.origin} ➔ {forecastData.route.destination}
                          </span>
                          <span className="fc-sub-window">
                            {forecastData.route.time_window} • {forecastData.forecast.weather_label.en}
                          </span>
                        </div>
                        <div className={`fc-grade-badge grade-${forecastData.forecast.risk_level.toLowerCase()}`}>
                          <span className="grade-letter">{forecastData.forecast.rating}</span>
                          <span className="grade-label">{forecastData.forecast.risk_level} Risk</span>
                        </div>
                      </div>

                      {/* Probability & Delay Gauges */}
                      <div className="fc-metrics-duo">
                        <div className="fc-metric-card delay-risk">
                          <span className="fc-met-label">Delay Probability</span>
                          <span className={`fc-met-val val-${forecastData.forecast.risk_level.toLowerCase()}`}>
                            {forecastData.forecast.delay_probability_pct}%
                          </span>
                          <div className="fc-meter-bar">
                            <div
                              className={`fc-meter-fill fill-${forecastData.forecast.risk_level.toLowerCase()}`}
                              style={{ width: `${forecastData.forecast.delay_probability_pct}%` }}
                            />
                          </div>
                        </div>

                        <div className="fc-metric-card on-time">
                          <span className="fc-met-label">Expected Average Delay</span>
                          <span className="fc-met-val text-cyan">
                            +{forecastData.forecast.expected_delay_minutes} min
                          </span>
                          <span className="fc-met-sub">
                            On-Time Chance: <strong>{forecastData.forecast.on_time_probability_pct}%</strong>
                          </span>
                        </div>
                      </div>

                      {/* Risk Factors Decomposition */}
                      <div className="fc-factor-decomposition">
                        <span className="decomp-title">Contributing Risk Breakdown:</span>
                        <div className="decomp-bars">
                          <div className="decomp-row">
                            <span className="d-label">Junction Congestion</span>
                            <div className="d-bar-track">
                              <div className="d-bar-fill fill-purple" style={{ width: `${forecastData.forecast.risk_factors.junction_congestion_pct}%` }} />
                            </div>
                            <span className="d-pct">{forecastData.forecast.risk_factors.junction_congestion_pct}%</span>
                          </div>
                          <div className="decomp-row">
                            <span className="d-label">Weather & Track Conditions</span>
                            <div className="d-bar-track">
                              <div className="d-bar-fill fill-sky" style={{ width: `${forecastData.forecast.risk_factors.weather_impact_pct}%` }} />
                            </div>
                            <span className="d-pct">{forecastData.forecast.risk_factors.weather_impact_pct}%</span>
                          </div>
                          <div className="decomp-row">
                            <span className="d-label">Time-of-Day Commute Load</span>
                            <div className="d-bar-track">
                              <div className="d-bar-fill fill-amber" style={{ width: `${forecastData.forecast.risk_factors.time_of_day_load_pct}%` }} />
                            </div>
                            <span className="d-pct">{forecastData.forecast.risk_factors.time_of_day_load_pct}%</span>
                          </div>
                          <div className="decomp-row">
                            <span className="d-label">Baseline Network Density</span>
                            <div className="d-bar-track">
                              <div className="d-bar-fill fill-slate" style={{ width: `${forecastData.forecast.risk_factors.baseline_network_load_pct}%` }} />
                            </div>
                            <span className="d-pct">{forecastData.forecast.risk_factors.baseline_network_load_pct}%</span>
                          </div>
                        </div>
                      </div>

                      {/* Bilingual Advisory Card */}
                      <div className="fc-advisory-box">
                        <div className="adv-lang-col">
                          <span className="adv-tag">🇬🇧 Travel Advisory:</span>
                          <p className="adv-text">{forecastData.forecast.advice.en}</p>
                        </div>
                        <div className="adv-lang-col de">
                          <span className="adv-tag">🇩🇪 Reisehinweis:</span>
                          <p className="adv-text">{forecastData.forecast.advice.de}</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="fc-error-box">
                      <span>{forecastError || 'Select parameters to generate forecast'}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Top 10 Best vs Top 10 Worst Comparison Cards */}
            <div className="db-top10-split-grid">
              {/* TOP 10 BEST */}
              <div className="db-top-card best-border">
                <div className="db-top-header">
                  <div>
                    <h3>🏆 Top 10 Most Punctual Main Stations</h3>
                    <span className="sub-tag-best">Cities &gt; 200k Population</span>
                  </div>
                  <span className="badge-best-pill">Most Reliable</span>
                </div>

                <div className="db-ranking-list">
                  {dbData?.top_10_best.map((st, i) => (
                    <div key={st.station} className="db-rank-row">
                      <div className="rank-left">
                        <span className="rank-num best">#{i + 1}</span>
                        <div>
                          <span className="station-hbf-name">{st.station}</span>
                          <span className="station-sub-city">{st.state} • {st.population.toLocaleString()} pop</span>
                        </div>
                      </div>
                      <div className="rank-right">
                        <div className="metric-col">
                          <span className="punct-pct best">{st.punctuality_pct}%</span>
                          <span className="punct-lbl">On-Time</span>
                        </div>
                        <div className="metric-col">
                          <span className="delay-min-tag">~{st.avg_delay_minutes} min</span>
                          <span className="punct-lbl">Avg Delay</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* TOP 10 WORST */}
              <div className="db-top-card worst-border">
                <div className="db-top-header">
                  <div>
                    <h3>⚠️ Top 10 Least Punctual / Most Delayed</h3>
                    <span className="sub-tag-worst">Cities &gt; 200k Population</span>
                  </div>
                  <span className="badge-worst-pill">Severe Congestion</span>
                </div>

                <div className="db-ranking-list">
                  {dbData?.top_10_worst.map((st, i) => (
                    <div key={st.station} className="db-rank-row">
                      <div className="rank-left">
                        <span className="rank-num worst">#{i + 1}</span>
                        <div>
                          <span className="station-hbf-name">{st.station}</span>
                          <span className="station-sub-city">{st.state} • {st.population.toLocaleString()} pop</span>
                        </div>
                      </div>
                      <div className="rank-right">
                        <div className="metric-col">
                          <span className="punct-pct worst">{st.not_punctual_pct}%</span>
                          <span className="punct-lbl">Delayed/Cancel</span>
                        </div>
                        <div className="metric-col">
                          <span className="delay-min-tag red">~{st.avg_delay_minutes} min</span>
                          <span className="punct-lbl">Avg Delay</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Detailed Delay Explorer & Distribution Table */}
            <div className="housing-section-card">
              <div className="section-title-row">
                <div>
                  <h3>All 40 Major German Rail Hubs (&gt;200k Pop) Delay Breakdown</h3>
                  <p className="sub-text-muted">
                    Delay Breakdown: &lt;5m (Green) | 5-15m (Yellow) | 15-30m (Orange) | &gt;30m (Rose) | Cancelled/Ausfall (Red, 120m penalty)
                  </p>
                </div>

                {/* Filters */}
                <div className="table-controls">
                  <div className="db-search-input">
                    <span>🔍</span>
                    <input
                      type="text"
                      placeholder="Search Hbf (e.g. Nürnberg, Köln, Berlin)..."
                      value={dbSearch}
                      onChange={(e) => setDbSearch(e.target.value)}
                    />
                  </div>

                  <div className="control-filter">
                    <span>State:</span>
                    <select value={dbStateFilter} onChange={(e) => setDbStateFilter(e.target.value)}>
                      {dbStatesList.map((st) => (
                        <option key={st} value={st}>
                          {st === 'All' ? 'All Federal States' : st}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="control-filter">
                    <span>Sort:</span>
                    <select value={dbSort} onChange={(e) => setDbSort(e.target.value)}>
                      <option value="punctuality">Most Punctual First</option>
                      <option value="worst">Least Punctual First</option>
                      <option value="delay">Highest Avg Delay</option>
                      <option value="trains">Train Traffic Volume</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Station Cards Grid */}
              <div className="db-stations-full-grid">
                {processedDbStations.map((st) => (
                  <div key={st.station} className="db-station-detail-card">
                    <div className="db-card-header">
                      <div>
                        <h4>{st.station}</h4>
                        <span className="db-state-info">{st.state} • {st.daily_trains} Trains/Day</span>
                      </div>
                      <div className="db-punct-score-badge">
                        <span className="score-val">{st.punctuality_pct}%</span>
                        <span className="score-lbl">Punctual</span>
                      </div>
                    </div>

                    {/* Delay Stacked Bar */}
                    <div className="stacked-delay-bar-container">
                      <div className="stacked-bar">
                        <div className="bar-seg seg-under5" style={{ width: `${st.delays.under_5min}%` }} title={`< 5m: ${st.delays.under_5min}%`} />
                        <div className="bar-seg seg-5-15" style={{ width: `${st.delays.min_5_to_15}%` }} title={`5-15m: ${st.delays.min_5_to_15}%`} />
                        <div className="bar-seg seg-15-30" style={{ width: `${st.delays.min_15_to_30}%` }} title={`15-30m: ${st.delays.min_15_to_30}%`} />
                        <div className="bar-seg seg-over30" style={{ width: `${st.delays.over_30min}%` }} title={`> 30m: ${st.delays.over_30min}%`} />
                        <div className="bar-seg seg-cancel" style={{ width: `${st.delays.cancelled}%` }} title={`Cancelled: ${st.delays.cancelled}%`} />
                      </div>
                    </div>

                    {/* Metric Details Breakdown */}
                    <div className="db-mini-metric-row">
                      <div className="m-item">
                        <span className="m-lbl">&lt;5 min</span>
                        <span className="m-val text-emerald">{st.delays.under_5min}%</span>
                      </div>
                      <div className="m-item">
                        <span className="m-lbl">5–15m</span>
                        <span className="m-val text-yellow">{st.delays.min_5_to_15}%</span>
                      </div>
                      <div className="m-item">
                        <span className="m-lbl">15–30m</span>
                        <span className="m-val text-orange">{st.delays.min_15_to_30}%</span>
                      </div>
                      <div className="m-item">
                        <span className="m-lbl">&gt;30m</span>
                        <span className="m-val text-rose">{st.delays.over_30min}%</span>
                      </div>
                      <div className="m-item">
                        <span className="m-lbl">Ausfall (2h)</span>
                        <span className="m-val text-red">{st.delays.cancelled}%</span>
                      </div>
                    </div>

                    <div className="db-card-footer">
                      <span>Not Punctual: <strong className="text-rose">{st.not_punctual_pct}%</strong></span>
                      <span>Weighted Avg Delay: <strong className="text-cyan">{st.avg_delay_minutes} min</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================
            TAB 3: GERMANY HOUSING & RENT INDEX
        ======================================================== */}
        {activeTab === 'housing' && (
          <div className="housing-container">
            <div className="section-header">
              <div className="header-badge-row">
                <span className="api-badge">Federal Statistical Benchmarks</span>
                <span className="cache-badge">Updated Q3 2026</span>
              </div>
              <h2>German Housing & Rental Market Analytics</h2>
              <p>Explore rent price indices across German metropolitan hubs, compute estimated monthly living costs, and analyze regional price dynamics.</p>
            </div>

            {/* KPI Summary Cards */}
            {housingData && (
              <div className="housing-kpi-grid">
                <div className="kpi-card">
                  <span className="kpi-label">National Avg Kaltmiete</span>
                  <span className="kpi-value text-cyan">{housingData.summary.national_avg_kaltmiete} €/m²</span>
                  <span className="kpi-sub">Cold rent baseline</span>
                </div>
                <div className="kpi-card">
                  <span className="kpi-label">National Avg Warmmiete</span>
                  <span className="kpi-value text-emerald">{housingData.summary.national_avg_warmmiete} €/m²</span>
                  <span className="kpi-sub">Including heating & utilities</span>
                </div>
                <div className="kpi-card">
                  <span className="kpi-label">Year-over-Year Growth</span>
                  <span className="kpi-value text-yellow">+{housingData.summary.yoy_national_growth}%</span>
                  <span className="kpi-sub">National average inflation</span>
                </div>
                <div className="kpi-card">
                  <span className="kpi-label">Highest City (Munich)</span>
                  <span className="kpi-value text-rose">{housingData.summary.top_city_kaltmiete.price} €/m²</span>
                  <span className="kpi-sub">Rank #1 in Germany</span>
                </div>
              </div>
            )}

            {/* Interactive Rent Calculator & Estimator */}
            <div className="rent-calculator-card">
              <div className="calc-header">
                <h3>🧮 Interactive German Rent Estimator</h3>
                <p>Calculate estimated cold rent, utilities (Nebenkosten), and recommended minimum net income for any apartment size.</p>
              </div>

              <div className="calc-inputs-grid">
                <div className="calc-group">
                  <label>Select City / Hub:</label>
                  <select value={calcCityId} onChange={(e) => setCalcCityId(e.target.value)}>
                    {housingData?.cities.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.city} ({c.state}) — {c.kaltmiete} €/m²
                      </option>
                    ))}
                  </select>
                </div>

                <div className="calc-group">
                  <div className="slider-label-row">
                    <label>Apartment Living Area:</label>
                    <span className="slider-val-badge">{calcSize} m²</span>
                  </div>
                  <input
                    type="range"
                    min="20"
                    max="160"
                    step="5"
                    value={calcSize}
                    onChange={(e) => setCalcSize(parseInt(e.target.value) || 50)}
                    className="calc-slider"
                  />
                  <div className="calc-size-presets">
                    {[30, 50, 65, 85, 110].map((s) => (
                      <button
                        key={s}
                        className={`size-preset-btn ${calcSize === s ? 'active' : ''}`}
                        onClick={() => setCalcSize(s)}
                      >
                        {s} m²
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Calculator Output Breakdown */}
              <div className="calc-results-grid">
                <div className="result-box">
                  <span className="res-title">Estimated Cold Rent (Kaltmiete)</span>
                  <span className="res-val">{calculatedRent.kalt} €<span className="per-month">/mo</span></span>
                  <span className="res-rate">Rate: {activeCalcCity?.kaltmiete} €/m²</span>
                </div>
                <div className="result-box">
                  <span className="res-title">Utilities & Heating (Nebenkosten)</span>
                  <span className="res-val text-cyan">~{calculatedRent.neben} €<span className="per-month">/mo</span></span>
                  <span className="res-rate">Avg: {activeCalcCity?.nebenkosten_m2} €/m²</span>
                </div>
                <div className="result-box highlight-warm">
                  <span className="res-title">Total Estimated Warm Rent</span>
                  <span className="res-val text-emerald">~{calculatedRent.warm} €<span className="per-month">/mo</span></span>
                  <span className="res-rate">Total Monthly Living Cost</span>
                </div>
                <div className="result-box">
                  <span className="res-title">Recommended Min. Net Income</span>
                  <span className="res-val text-yellow">~{calculatedRent.minIncome} €<span className="per-month">/mo</span></span>
                  <span className="res-rate">30% Max Rent Rule</span>
                </div>
              </div>
            </div>

            {/* City Comparison Table & Rankings */}
            <div className="housing-section-card">
              <div className="section-title-row">
                <h3>Major German Cities Rent Index Comparison</h3>
                <div className="table-controls">
                  <div className="control-filter">
                    <span>Region:</span>
                    {['All', 'South', 'West', 'North', 'East'].map((r) => (
                      <button
                        key={r}
                        type="button"
                        className={`region-btn ${housingRegion === r ? 'active' : ''}`}
                        onClick={() => setHousingRegion(r)}
                      >
                        {r}
                      </button>
                    ))}
                  </div>

                  <div className="control-filter">
                    <span>Sort:</span>
                    <select value={housingSort} onChange={(e) => setHousingSort(e.target.value)}>
                      <option value="kaltmiete">Highest Kaltmiete</option>
                      <option value="warmmiete">Highest Warmmiete</option>
                      <option value="growth">Highest YoY Growth</option>
                      <option value="burden">Rent Burden %</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="city-cards-grid">
                {processedHousingCities.map((c) => (
                  <div key={c.id} className="city-rent-card">
                    <div className="city-card-top">
                      <div>
                        <h4>{c.city}</h4>
                        <span className="city-state-tag">{c.state} • {c.region}</span>
                      </div>
                      <span className="rank-badge">#{c.index_rank}</span>
                    </div>

                    <div className="city-price-metrics">
                      <div className="c-metric">
                        <span className="c-label">Kaltmiete</span>
                        <span className="c-val">{c.kaltmiete} €/m²</span>
                      </div>
                      <div className="c-metric">
                        <span className="c-label">Warmmiete</span>
                        <span className="c-val text-emerald">{c.warmmiete} €/m²</span>
                      </div>
                      <div className="c-metric">
                        <span className="c-label">YoY Growth</span>
                        <span className="c-val text-yellow">+{c.yoy_growth}%</span>
                      </div>
                    </div>

                    <div className="benchmark-bar-wrap">
                      <div className="benchmark-info">
                        <span>Price Index vs Benchmark</span>
                        <span>{Math.round((c.kaltmiete / 21.8) * 100)}%</span>
                      </div>
                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{ width: `${(c.kaltmiete / 21.8) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 16 Federal States (Bundesländer) Overview */}
            <div className="housing-section-card">
              <div className="section-title-row">
                <h3>16 German Federal States (Bundesländer) Rent Overview</h3>
                <span className="sub-tag">State-level Weighted Averages</span>
              </div>
              <div className="states-grid">
                {housingData?.states.map((st) => (
                  <div key={st.state} className="state-card">
                    <div className="state-card-header">
                      <span className="state-name">{st.state}</span>
                      <span className="state-trend">{st.trend}</span>
                    </div>
                    <div className="state-price-row">
                      <span className="state-val">{st.avg_kaltmiete} €</span>
                      <span className="state-unit">/m² avg</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================
            TAB 4: TECH JOBS RADAR (GERMANY)
        ======================================================== */}
        {activeTab === 'jobs' && (
          <div className="jobs-container">
            <div className="section-header">
              <div className="header-badge-row">
                <span className="api-badge">Arbeitnow & JobSpy Engine</span>
                <span className="ssl-badge">🇩🇪 Germany Tech Market</span>
                <span className="cache-badge">⚡ English-Friendly (No C1/C2 Gatekeeping)</span>
              </div>
              <h2>Tech Jobs Radar Germany</h2>
              <p>
                Live English-friendly tech opportunities across Germany filtered in real-time. Excludes strict German fluency hurdles (C1, C2, verhandlungssicher, fließend) for international data, engineering & software professionals.
              </p>
            </div>

            {/* Filter Controls Panel */}
            <div className="jobs-control-panel">
              <form
                className="jobs-search-form"
                onSubmit={(e) => {
                  e.preventDefault()
                  fetchJobs(searchKeyword, selectedHours)
                }}
              >
                <div className="jobs-search-input-wrap">
                  <span className="search-icon">🔍</span>
                  <input
                    type="text"
                    placeholder="Search job title or keyword (e.g. Data Analyst, Data Engineer, Python, React)..."
                    value={searchKeyword}
                    onChange={(e) => setSearchKeyword(e.target.value)}
                  />
                  {searchKeyword && (
                    <button
                      type="button"
                      className="clear-btn"
                      onClick={() => setSearchKeyword('')}
                    >
                      ✕
                    </button>
                  )}
                </div>

                <div className="hours-toggle-group">
                  <span className="hours-label">Lookback:</span>
                  {[12, 24, 72].map((h) => (
                    <button
                      key={h}
                      type="button"
                      className={`hour-btn ${selectedHours === h ? 'active' : ''}`}
                      onClick={() => {
                        setSelectedHours(h)
                        fetchJobs(searchKeyword, h)
                      }}
                    >
                      {h}h
                    </button>
                  ))}
                </div>

                <button
                  type="submit"
                  className="jobs-action-btn search"
                  disabled={jobsLoading}
                >
                  {jobsLoading ? 'Searching...' : 'Search Jobs'}
                </button>

                <button
                  type="button"
                  className="jobs-action-btn refresh"
                  onClick={() => fetchJobs(searchKeyword, selectedHours)}
                  disabled={jobsLoading}
                >
                  🔄 Refresh
                </button>
              </form>

              {/* Quick Keyword Pills */}
              <div className="city-pills-row">
                <span className="pills-label">Popular Searches:</span>
                {['Data Analyst', 'Data Engineer', 'Python', 'Data Scientist', 'Machine Learning', 'Full Stack'].map((kw) => (
                  <button
                    key={kw}
                    className={`city-pill ${searchKeyword === kw ? 'active' : ''}`}
                    onClick={() => {
                      setSearchKeyword(kw)
                      fetchJobs(kw, selectedHours)
                    }}
                  >
                    {kw}
                  </button>
                ))}
              </div>
            </div>

            {/* Jobs Stats Summary Bar */}
            <div className="analytics-summary-bar">
              <div className="summary-stat">
                <span className="stat-label">Active Keyword</span>
                <span className="stat-value text-cyan">{searchKeyword || 'All Tech'}</span>
              </div>
              <div className="summary-stat">
                <span className="stat-label">Timeframe</span>
                <span className="stat-value text-emerald">Past {selectedHours} Hours</span>
              </div>
              <div className="summary-stat">
                <span className="stat-label">Matching Listings</span>
                <span className="stat-value text-emerald">{jobs.length} Jobs Found</span>
              </div>
              <div className="summary-stat">
                <span className="stat-label">Language Requirement</span>
                <span className="stat-value text-cyan">English-Friendly</span>
              </div>
            </div>

            {/* Error Message */}
            {jobsError && <div className="error-msg">⚠️ {jobsError}</div>}

            {/* Loading Indicator */}
            {jobsLoading && (
              <div className="status-msg">
                🔍 Searching live tech job boards and filtering English-friendly roles...
              </div>
            )}

            {/* Empty State */}
            {!jobsLoading && jobs.length === 0 && !jobsError && (
              <div className="no-data">
                No tech jobs found for "{searchKeyword}" within the last {selectedHours} hours. Try selecting 72h or searching with another keyword.
              </div>
            )}

            {/* Job Cards Grid */}
            <div className="jobs-cards-grid">
              {jobs.map((job, idx) => (
                <div key={idx} className="job-card">
                  <div className="job-card-top">
                    <div className="job-title-wrap">
                      <h4 className="job-title">{job.title}</h4>
                      <div className="job-company-row">
                        <span className="job-company">🏢 {job.company}</span>
                        <span className="job-location">📍 {job.location}</span>
                      </div>
                    </div>
                    <span className={`job-source-badge ${job.source?.toLowerCase()}`}>
                      {job.source || 'Aggregator'}
                    </span>
                  </div>

                  <div className="job-card-bottom">
                    <div className="job-posted-time">
                      <span>⏱️ {job.posted_at}</span>
                      <span className="job-verified-tag">✓ English Friendly</span>
                    </div>
                    <a
                      href={job.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="job-apply-btn"
                    >
                      Apply Now ↗
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ========================================================
            TAB 5: ENERGY & MARKETS (CRUDE OIL, CYCLES, RENEWABLES)
        ======================================================== */}
        {activeTab === 'dashboard' && (
          <div className="dashboard-view">
            <div className="section-header">
              <div className="header-badge-row">
                <span className="api-badge">PySpark Processed Data</span>
                <span className="ssl-badge">Commodities & Energy Grid</span>
              </div>
              <h2>German Energy Markets & Mobility Analytics Overview</h2>
              <p>Time-series analysis of crude oil pricing, daily fuel price fluctuation cycles, and Germany's renewable power generation mix.</p>
            </div>

            {/* Best Time of Day to Refuel Guide Card */}
            <div className="refuel-cycle-card">
              <div className="refuel-header">
                <div>
                  <h3>⏰ Best Time of Day to Refuel in Germany</h3>
                  <p>In Germany, fuel prices fluctuate systematically up to 15-20 cents/liter throughout 24 hours.</p>
                </div>
                <div className="optimal-window-badge">
                  <span className="opt-title">Recommended Window:</span>
                  <span className="opt-time">18:00 – 21:00 (Save ~€8 per Tank)</span>
                </div>
              </div>

              {/* 24-Hour Cycle Visualizer */}
              <div className="hourly-cycle-bar">
                {[
                  { hour: '06:00', price: 'High (+12c)', type: 'peak' },
                  { hour: '08:00', price: 'Peak (+15c)', type: 'peak' },
                  { hour: '10:00', price: 'Mid (+7c)', type: 'mid' },
                  { hour: '12:00', price: 'Dip (-4c)', type: 'low' },
                  { hour: '14:00', price: 'Mid (+3c)', type: 'mid' },
                  { hour: '16:00', price: 'Drop (-6c)', type: 'low' },
                  { hour: '18:00', price: 'Lowest (-12c)', type: 'optimal' },
                  { hour: '20:00', price: 'Lowest (-14c)', type: 'optimal' },
                  { hour: '22:00', price: 'High (+10c)', type: 'peak' },
                  { hour: '02:00', price: 'Night Peak (+18c)', type: 'peak' },
                ].map((item, idx) => (
                  <div key={idx} className={`cycle-node ${item.type}`}>
                    <span className="node-time">{item.hour}</span>
                    <span className="node-status">{item.price}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Crude Oil Pipeline & Market Data Grid */}
            <div className="dashboard-grid">
              {/* Widget 1: Tech Jobs Radar Summary */}
              <div className="widget-card interactive" onClick={() => navigateTo('jobs')}>
                <div className="widget-header">
                  <h3>Latest Tech Jobs in Germany</h3>
                  <span className="widget-tag live">LIVE RADAR</span>
                </div>
                <div className="widget-body">
                  <div className="metric-highlight">
                    <span className="metric-value">{jobs.length > 0 ? `${jobs.length}` : '25+'}</span>
                    <span className="metric-label">English-Friendly Openings (Past {selectedHours}h)</span>
                  </div>
                  <p className="widget-action-link">Open Tech Jobs Radar & Filter by Role →</p>
                </div>
              </div>

              {/* Widget 2: Crude Oil Overview */}
              <div className="widget-card">
                <div className="widget-header">
                  <h3>Crude Oil Market (WTI)</h3>
                  <span className="widget-tag">PySpark Pipeline</span>
                </div>
                <div className="widget-body">
                  {latestOil ? (
                    <div className="metric-highlight">
                      <span className="metric-value">${latestOil.Close || latestOil.price}</span>
                      <span className="metric-label">Latest Close Price (USD/bbl)</span>
                    </div>
                  ) : (
                    <p className="placeholder-text">Loading oil metrics...</p>
                  )}
                  <p className="widget-footer-text">
                    PySpark 7-Day Moving Average: ${latestOil?.SMA_5 || latestOil?.sma_7 || latestOil?.Close || '-'}
                  </p>
                </div>
              </div>

              {/* Widget 3: Germany Renewable Grid Share */}
              <div className="widget-card">
                <div className="widget-header">
                  <h3>Germany Renewable Power Grid</h3>
                  <span className="widget-tag live">SMARD OpenData</span>
                </div>
                <div className="widget-body">
                  <div className="grid-mix-bars">
                    <div className="mix-item">
                      <span>Wind Power (On/Offshore)</span>
                      <strong>42.4%</strong>
                    </div>
                    <div className="mix-item">
                      <span>Solar Photovoltaic</span>
                      <strong>28.1%</strong>
                    </div>
                    <div className="mix-item">
                      <span>Biomass & Hydro</span>
                      <strong>12.5%</strong>
                    </div>
                    <div className="mix-item">
                      <span>Conventional (Gas/Coal)</span>
                      <strong>17.0%</strong>
                    </div>
                  </div>
                  <p className="widget-action-link">Total Clean Power: 83.0% of German Grid</p>
                </div>
              </div>

              {/* Widget 4: Live Fuel Summary */}
              <div className="widget-card interactive" onClick={() => navigateTo('fuel')}>
                <div className="widget-header">
                  <h3>Regional Fuel Average ({locationName})</h3>
                  <span className="widget-tag live">LIVE MTS-K</span>
                </div>
                <div className="widget-body">
                  <div className="metric-row">
                    <div>
                      <span className="metric-sublabel">Super E5</span>
                      <div className="metric-sm">
                        {analytics?.avg_e5 ? `${analytics.avg_e5.toFixed(3)} €` : 'Loading...'}
                      </div>
                    </div>
                    <div>
                      <span className="metric-sublabel">Diesel</span>
                      <div className="metric-sm">
                        {analytics?.avg_diesel ? `${analytics.avg_diesel.toFixed(3)} €` : 'Loading...'}
                      </div>
                    </div>
                  </div>
                  <p className="widget-action-link">Open Interactive Fuel Map & Radius Explorer →</p>
                </div>
              </div>

              {/* Widget 5: DB Train Mobility */}
              <div className="widget-card interactive" onClick={() => navigateTo('trains')}>
                <div className="widget-header">
                  <h3>DB Rail Punctuality Tracker</h3>
                  <span className="widget-tag live">40 Bahnhöfe</span>
                </div>
                <div className="widget-body">
                  <div className="metric-highlight">
                    <span className="metric-value">73.2%</span>
                    <span className="metric-label">National Average On-Time Rate</span>
                  </div>
                  <p className="widget-action-link">Explore Best & Worst 10 Bahnhöfe →</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================
            TAB 5: PORTFOLIO & RESUME (HOSEIN MADANI)
        ======================================================== */}
        {activeTab === 'portfolio' && (
          <div className="portfolio-container">
            {/* Hero Profile Card */}
            <div className="portfolio-hero-card">
              <div className="hero-main-info">
                <div className="hero-badge-pill">
                  <span className="pulse-dot-green"></span>
                  Based in Nuremberg & Erlangen, Germany
                </div>
                <h1>Hosein Madani</h1>
                <h2>Data Analyst & Biomedical Data Engineer</h2>
                <p className="hero-bio">
                  Data Analyst with comprehensive hands-on expertise in complex data analysis, data pipelines, and machine learning. Proficient in Python, PySpark, SQL, and R for automated end-to-end analytics workflows, high-dimensional biomedical modeling, and cloud deployments.
                </p>

                <div className="hero-cta-row">
                  <a
                    href="https://www.linkedin.com/in/hossein-madani-f"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="portfolio-btn primary"
                  >
                    🔗 LinkedIn Profile
                  </a>
                  <a href="mailto:hoseinmadani74@gmail.com" className="portfolio-btn secondary">
                    ✉️ hoseinmadani74@gmail.com
                  </a>
                  <button onClick={() => window.print()} className="portfolio-btn print-cv-btn">
                    📄 Print / Save CV (PDF)
                  </button>
                  <span className="portfolio-phone-tag">📞 +49 157 5364 3274</span>
                </div>
              </div>

              <div className="hero-meta-box">
                <div className="meta-item">
                  <span className="meta-title">Languages</span>
                  <span className="meta-val">English (C1) • German (B1)</span>
                </div>
                <div className="meta-item">
                  <span className="meta-title">Degree</span>
                  <span className="meta-val">M.Sc. Data Processing (FAU)</span>
                </div>
                <div className="meta-item">
                  <span className="meta-title">Specialization</span>
                  <span className="meta-val">Data Engineering & Analytics</span>
                </div>
              </div>
            </div>

            {/* Interactive Production System Architecture Diagram */}
            <div className="portfolio-section">
              <div className="section-title-row">
                <div>
                  <h3>Production System Architecture (DatenLens.de)</h3>
                  <span className="sub-tag">End-to-End Real-Time Pipeline</span>
                </div>
              </div>

              <div className="architecture-flow-wrapper">
                <div className="arch-step">
                  <div className="arch-step-box">
                    <span className="arch-icon">🌐</span>
                    <h5>Data Ingestion</h5>
                    <p>MTS-K Fuel Stream, DB OpenData & Yahoo Finance APIs</p>
                  </div>
                  <span className="arch-arrow">→</span>
                </div>

                <div className="arch-step">
                  <div className="arch-step-box highlight">
                    <span className="arch-icon">⚡</span>
                    <h5>FastAPI & TTL Cache</h5>
                    <p>In-memory spatial caching & dynamic analytics computation</p>
                  </div>
                  <span className="arch-arrow">→</span>
                </div>

                <div className="arch-step">
                  <div className="arch-step-box">
                    <span className="arch-icon">🔥</span>
                    <h5>PySpark Engine</h5>
                    <p>7-Day rolling window time-series calculations & aggregations</p>
                  </div>
                  <span className="arch-arrow">→</span>
                </div>

                <div className="arch-step">
                  <div className="arch-step-box highlight">
                    <span className="arch-icon">🐳</span>
                    <h5>Docker & Nginx TLS</h5>
                    <p>Multi-stage containers on AWS EC2 with Let's Encrypt SSL</p>
                  </div>
                  <span className="arch-arrow">→</span>
                </div>

                <div className="arch-step">
                  <div className="arch-step-box">
                    <span className="arch-icon">🗺️</span>
                    <h5>React & Leaflet GIS</h5>
                    <p>Interactive spatial mapping, geocoding & GPS detection</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Technical Skills & Capabilities Grid */}
            <div className="portfolio-section">
              <div className="section-title-row">
                <h3>Technical Capabilities & Toolstack</h3>
                <span className="sub-tag">Production Stack</span>
              </div>

              <div className="skills-matrix-grid">
                {/* Category 1 */}
                <div className="skill-card">
                  <div className="skill-icon text-cyan">💻</div>
                  <h4>Languages & APIs</h4>
                  <p>Python (Proficient), R (Proficient), SQL (PostgreSQL, MySQL), Cypher (Neo4j), JavaScript (ES6+), FastAPI, C/C++, HTML5/CSS3</p>
                  <div className="skill-tags">
                    <span>Python</span>
                    <span>SQL</span>
                    <span>R</span>
                    <span>FastAPI</span>
                    <span>JavaScript</span>
                  </div>
                </div>

                {/* Category 2 */}
                <div className="skill-card">
                  <div className="skill-icon text-emerald">☁️</div>
                  <h4>Data Engineering & Cloud</h4>
                  <p>Apache Spark (PySpark), In-Memory Caching (TTL), Docker Containers, AWS EC2, Nginx Reverse Proxy, SSL/TLS (Let's Encrypt), Linux/WSL, Bash, Git/CI-CD</p>
                  <div className="skill-tags">
                    <span>PySpark</span>
                    <span>Docker</span>
                    <span>AWS EC2</span>
                    <span>Nginx SSL</span>
                    <span>Bash</span>
                  </div>
                </div>

                {/* Category 3 */}
                <div className="skill-card">
                  <div className="skill-icon text-yellow">📊</div>
                  <h4>Analytics, ML & GIS</h4>
                  <p>TensorFlow, Keras, Scikit-Learn, Pandas, NumPy, Seurat, Power BI, Leaflet.js GIS, Time-Series Window Analytics, MS Excel</p>
                  <div className="skill-tags">
                    <span>Scikit-Learn</span>
                    <span>Leaflet GIS</span>
                    <span>Power BI</span>
                    <span>TensorFlow</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Featured Engineering Projects */}
            <div className="portfolio-section">
              <div className="section-title-row">
                <h3>Featured Engineering & Analytics Projects</h3>
                <span className="sub-tag">Live Implementations</span>
              </div>

              <div className="projects-grid">
                {/* Project 1 */}
                <div className="project-card featured">
                  <div className="proj-header">
                    <h4>DatenLens.de — German Mobility & Energy Engine</h4>
                    <span className="proj-status live">LIVE ON AWS</span>
                  </div>
                  <p className="proj-desc">
                    Full-stack production real-time analytics platform deployed at <a href="https://datenlens.de" target="_blank" rel="noopener noreferrer">datenlens.de</a> on AWS EC2. Integrates German MTS-K fuel prices with 5-min in-memory TTL caching, interactive Leaflet GIS map with GPS location detection, PySpark rolling time-series market pipeline, DB train punctuality engine, and Let's Encrypt SSL.
                  </p>
                  <div className="proj-tags">
                    <span>FastAPI</span>
                    <span>PySpark</span>
                    <span>Docker</span>
                    <span>AWS EC2</span>
                    <span>Leaflet GIS</span>
                    <span>Nginx SSL</span>
                  </div>
                </div>

                {/* Project 2 */}
                <div className="project-card">
                  <div className="proj-header">
                    <h4>Automotive Graph Database & Variant Engine</h4>
                    <span className="proj-status">ABIDAT GmbH</span>
                  </div>
                  <p className="proj-desc">
                    Designed graph data models in Neo4j and developed automated Python & SQL pipelines to evaluate complex mathematical/logical relationships in vehicle variant management for a leading German automotive manufacturer.
                  </p>
                  <div className="proj-tags">
                    <span>Neo4j</span>
                    <span>Python</span>
                    <span>SQL</span>
                    <span>Docker</span>
                    <span>Linux/WSL</span>
                  </div>
                </div>

                {/* Project 3 */}
                <div className="project-card">
                  <div className="proj-header">
                    <h4>Single-Cell RNA Sequencing Arthritis Pipeline</h4>
                    <span className="proj-status">Univ. Clinic Erlangen</span>
                  </div>
                  <p className="proj-desc">
                    Master thesis data pipeline for pre-processing, normalization, dimensionality reduction (PCA, UMAP), cell clustering, and differential expression analysis across arthritis conditions using R (Seurat) and Python.
                  </p>
                  <div className="proj-tags">
                    <span>R / Seurat</span>
                    <span>Python</span>
                    <span>PCA / UMAP</span>
                    <span>Biomedical Data</span>
                  </div>
                </div>

                {/* Project 4 */}
                <div className="project-card">
                  <div className="proj-header">
                    <h4>Neural Network Plantar Pressure Classifier</h4>
                    <span className="proj-status">Robotics Lab FUM</span>
                  </div>
                  <p className="proj-desc">
                    Developed Neural Network architectures in TensorFlow/Keras analyzing 600,000 ground reaction sensor data points collected via STM32 ARM hardware for biomechanical pressure prediction.
                  </p>
                  <div className="proj-tags">
                    <span>TensorFlow</span>
                    <span>Keras</span>
                    <span>Signal Processing</span>
                    <span>STM32</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Career Journey */}
            <div className="portfolio-section">
              <div className="section-title-row">
                <h3>Professional Experience</h3>
                <span className="sub-tag">Career History</span>
              </div>

              <div className="timeline-experience-list">
                <div className="exp-item">
                  <div className="exp-top">
                    <div>
                      <h4>Master's Thesis Student — Biomedical Data Engineering</h4>
                      <span className="exp-company">University Clinic of Erlangen | Erlangen, Germany</span>
                    </div>
                    <span className="exp-date">01/2025 – 10/2025</span>
                  </div>
                  <p className="exp-thesis">Thesis: "Data Analysis of Fibroblast in Arthritis: A Single-Cell RNA Sequencing Study"</p>
                  <ul className="exp-bullets">
                    <li>Developed automated high-dimensional data analysis pipelines for quality control, normalization, and scaling.</li>
                    <li>Executed multi-sample integration, PCA, UMAP, and differential cell composition analysis.</li>
                  </ul>
                </div>

                <div className="exp-item">
                  <div className="exp-top">
                    <div>
                      <h4>Data Analyst</h4>
                      <span className="exp-company">ABIDAT GmbH | Nuremberg, Germany</span>
                    </div>
                    <span className="exp-date">10/2022 – 01/2024</span>
                  </div>
                  <ul className="exp-bullets">
                    <li>Developed ETL and transformation workflows in Python for CSV, JSON, and XML streams.</li>
                    <li>Constructed and optimized Neo4j graph databases with SQL and Python scripting for automotive variant management.</li>
                    <li>Worked with Ubuntu WSL, Docker containers, and automated bash scripting.</li>
                  </ul>
                </div>

                <div className="exp-item">
                  <div className="exp-top">
                    <div>
                      <h4>AI / ML Engineer & Researcher</h4>
                      <span className="exp-company">Robotics Laboratory of Ferdowsi University</span>
                    </div>
                    <span className="exp-date">09/2020 – 02/2021</span>
                  </div>
                  <ul className="exp-bullets">
                    <li>Constructed deep learning prediction models in TensorFlow/Keras on 600,000 data points.</li>
                    <li>Engineered sensor insoles and hardware signal acquisition with ARM microcontrollers.</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Education */}
            <div className="portfolio-section">
              <div className="section-title-row">
                <h3>Academic Education</h3>
                <span className="sub-tag">Degrees</span>
              </div>

              <div className="education-grid">
                <div className="edu-card">
                  <span className="edu-date">10/2021 – 06/2026</span>
                  <h4>M.Sc. Medical Imaging & Data Processing</h4>
                  <span className="edu-school">Friedrich-Alexander-Universität Erlangen-Nürnberg (FAU)</span>
                  <p>Focus: Applied Data Science, Pattern Recognition, Machine Learning, Computer Vision.</p>
                </div>
                <div className="edu-card">
                  <span className="edu-date">09/2015 – 09/2020</span>
                  <h4>B.Sc. Electrical Engineering (Biomedical)</h4>
                  <span className="edu-school">Ferdowsi University of Mashhad</span>
                  <p>GPA: 2.5 (German System) • Ranked in Top 3% in National Entrance Exam (2015).</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}




