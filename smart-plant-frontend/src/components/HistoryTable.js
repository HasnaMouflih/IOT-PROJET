import React, { useState, useEffect } from "react";
import { DataGrid } from "@mui/x-data-grid";
import { useDemoData } from '@mui/x-data-grid-generator';
import CircularProgress from "@mui/material/CircularProgress";
import axios from "axios";

export default function PlantHistoryGrid() {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPlants = async () => {
      try {
        const res = await axios.get("http://localhost:9000/api/plants");
        setPlants(res.data);
      } catch (err) {
        console.error("Erreur lors de la récupération des plantes :", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPlants();
  }, []);

  // Flatten history list
  const allHistory = [];
  plants.forEach((plant) => {
    plant.history?.forEach((h) =>
      allHistory.push({ ...h, plantName: plant.name })
    );
  });

    const columns = [
      { field: "plantName", headerName: "Plante", flex: 1 ,   hideable: true,
    renderCell: (params) => params.value,
    sx: { display: { xs: "none", sm: "block" } }
  },
      { field: "time", headerName: "Heure", flex: 1 ,   hideable: true,
    renderCell: (params) => params.value,
    sx: { display: { xs: "none", sm: "block" } }
  },
      { field: "humidity", headerName: "Humidité", flex: 1 ,   hideable: true,
    renderCell: (params) => params.value,
    sx: { display: { xs: "none", sm: "block" } }
  },
      { field: "temperature", headerName: "Température", flex: 1 ,   hideable: true,
    renderCell: (params) => params.value,
    sx: { display: { xs: "none", sm: "block" } }
  },
      { field: "light", headerName: "Lumière", flex: 1 ,   hideable: true,
    renderCell: (params) => params.value,
    sx: { display: { xs: "none", sm: "block" } }
  },
      { field: "soilMoisture", headerName: "Humidité du sol", flex: 1,    hideable: true,
    renderCell: (params) => params.value,
    sx: { display: { xs: "none", sm: "block" } }
  },
      { field: "emotion", headerName: "Émotion", flex: 1  ,  hideable: true,
      renderCell: (params) => params.value,
      sx: { display: { xs: "none", sm: "block" } }
    },
    ];


  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", marginTop: 50 }}>
        <CircularProgress size={40} color="success" />
      </div>
    );
  }

  return (
    <div style={{ height: 450, width: "100%" }}>
      <DataGrid
        rows={allHistory.map((h, index) => ({ id: index, ...h }))}
        columns={columns}
        showToolbar
        pageSizeOptions={[5, 10, 20]}
        initialState={{
          pagination: { paginationModel: { pageSize: 10 } },
        }}
      />
    </div>
  );
}
