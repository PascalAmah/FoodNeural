// import React from "react";
// import {
//   BarChart,
//   Bar,
//   XAxis,
//   YAxis,
//   Tooltip,
//   Legend,
//   ResponsiveContainer,
// } from "recharts";
// import { motion as Motion } from "framer-motion";

// const ImpactChart = ({ impactData }) => {
//   if (!impactData) return null;

//   const chartData = [
//     { name: "Carbon (kg CO₂)", value: impactData.carbon },
//     { name: "Water (L)", value: impactData.water },
//     { name: "Energy (kWh)", value: impactData.energy },
//     { name: "Waste (kg)", value: impactData.waste },
//     { name: "Deforestation (ha)", value: impactData.deforestation || 0 },
//   ];

//   const getBarColor = () => {
//     switch (impactData.impact) {
//       case "High":
//         return "#ff6b6b";
//       case "Medium":
//         return "#feca57";
//       case "Low":
//         return "#1dd1a1";
//       default:
//         return "#82ca9d";
//     }
//   };

//   const containerVariants = {
//     hidden: { opacity: 0, y: 20 },
//     visible: { opacity: 1, y: 0 },
//   };

//   return (
//     <Motion.div
//       variants={containerVariants}
//       initial="hidden"
//       animate="visible"
//       transition={{ duration: 0.5 }}
//       className="bg-white p-6 rounded-xl shadow-lg"
//     >
//       <h3 className="text-xl font-semibold text-gray-800 mb-4">
//         Environmental Impact
//       </h3>
//       <div className="flex items-center gap-2 mb-6">
//         <span className="text-gray-600">Impact Level:</span>
//         <span
//           className={`px-3 py-1 rounded-full text-sm font-medium text-white
//           ${
//             impactData.impact === "High"
//               ? "bg-red-500"
//               : impactData.impact === "Medium"
//               ? "bg-yellow-500"
//               : "bg-green-500"
//           }`}
//         >
//           {impactData.impact}
//         </span>
//       </div>
//       <ResponsiveContainer width="100%" height={300}>
//         <BarChart data={chartData}>
//           <XAxis dataKey="name" />
//           <YAxis />
//           <Tooltip />
//           <Legend />
//           <Bar dataKey="value" fill={getBarColor()} />
//         </BarChart>
//       </ResponsiveContainer>
//     </Motion.div>
//   );
// };

// export default ImpactChart;

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
} from "recharts";
import { motion as Motion } from "framer-motion";
import {
  GiFruitBowl,
  GiEnergyTank,
  GiTrashCan,
  GiTreeDoor,
  GiWaterDrop,
} from "react-icons/gi"; // Icons for visual enhancement

const ImpactChart = ({ impactData }) => {
  if (!impactData) return null;

  // Data for bar chart (excluding water)
  const barData = [
    {
      name: "Carbon (kg CO₂)",
      value: impactData.carbon,
      icon: <GiFruitBowl />,
    },
    { name: "Energy (kWh)", value: impactData.energy, icon: <GiEnergyTank /> },
    { name: "Waste (kg)", value: impactData.waste, icon: <GiTrashCan /> },
    {
      name: "Deforestation (ha)",
      value: impactData.deforestation || 0,
      icon: <GiTreeDoor />,
    },
  ];

  // Data for water (radial bar chart)
  const waterData = [
    { name: "Water (L)", value: impactData.water, fill: "#60a5fa" }, // Blue color for water
  ];

  // Data for pie chart (impact distribution, including water)
  const totalImpact =
    impactData.carbon +
    impactData.water +
    impactData.energy +
    impactData.waste +
    (impactData.deforestation || 0);
  const pieData = [
    {
      name: "Carbon",
      value: totalImpact > 0 ? (impactData.carbon / totalImpact) * 100 : 0,
    },
    {
      name: "Water",
      value: totalImpact > 0 ? (impactData.water / totalImpact) * 100 : 0,
    },
    {
      name: "Energy",
      value: totalImpact > 0 ? (impactData.energy / totalImpact) * 100 : 0,
    },
    {
      name: "Waste",
      value: totalImpact > 0 ? (impactData.waste / totalImpact) * 100 : 0,
    },
    {
      name: "Deforestation",
      value:
        totalImpact > 0
          ? ((impactData.deforestation || 0) / totalImpact) * 100
          : 0,
    },
  ];

  const COLORS = ["#ff6b6b", "#60a5fa", "#feca57", "#82ca9d", "#ff9f43"]; // Color palette

  const getBarColor = () => {
    switch (impactData.impact) {
      case "High":
        return "#ff6b6b";
      case "Medium":
        return "#feca57";
      case "Low":
        return "#1dd1a1";
      default:
        return "#82ca9d";
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <Motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      transition={{ duration: 0.5 }}
      className="bg-white p-6 rounded-xl shadow-lg"
    >
      <h3 className="text-xl font-semibold text-gray-800 mb-4">
        Environmental Impact
      </h3>
      <div className="flex items-center gap-2 mb-6">
        <span className="text-gray-600">Impact Level:</span>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium text-white ${
            impactData.impact === "High"
              ? "bg-red-500"
              : impactData.impact === "Medium"
              ? "bg-yellow-500"
              : "bg-green-500"
          }`}
        >
          {impactData.impact}
        </span>
      </div>

      {/* Water Usage Section - Radial Bar Chart */}
      <div className="mb-8">
        <h4 className="text-md font-medium text-gray-700 mb-2 flex items-center gap-2">
          <GiWaterDrop className="text-blue-500" /> Water Usage
        </h4>
        <div className="flex items-center gap-4">
          <ResponsiveContainer width="30%" height={200}>
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="40%"
              outerRadius="80%"
              barSize={20}
              data={waterData}
            >
              <RadialBar
                minAngle={15}
                background
                clockWise
                dataKey="value"
                cornerRadius={10}
              >
                {waterData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </RadialBar>
              <Tooltip formatter={(value) => `${value} L`} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="text-blue-600 font-medium text-lg">
            {impactData.water.toLocaleString()} L
          </div>
        </div>
      </div>

      {/* Bar Chart Section (Other Metrics) */}
      <div className="mb-8">
        <h4 className="text-md font-medium text-gray-700 mb-2">
          Other Impact Metrics
        </h4>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={barData}>
            <XAxis
              dataKey="name"
              tick={<CustomizedAxisTick />}
              interval={0}
              angle={-45}
              textAnchor="end"
              height={70}
            />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill={getBarColor()}>
              {barData.map((entry, index) => (
                <Cell key={`cell-${index}`} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Donut Chart Section (Impact Distribution) */}
      <div>
        <h4 className="text-md font-medium text-gray-700 mb-2">
          Impact Distribution
        </h4>
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
            >
              {pieData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Motion.div>
  );
};

// Custom XAxis tick component to include icons
const CustomizedAxisTick = ({ x, y, payload }) => {
  const icon = payload.value.split(" (")[0]; // Extract name before unit
  return (
    <g transform={`translate(${x},${y})`}>
      <text
        x={0}
        y={0}
        dy={16}
        textAnchor="end"
        fill="#666"
        transform="rotate(-45)"
      >
        {payload.value}
      </text>
      {icon === "Carbon" && <GiFruitBowl className="text-orange-500" />}
      {icon === "Energy" && <GiEnergyTank className="text-yellow-500" />}
      {icon === "Waste" && <GiTrashCan className="text-gray-500" />}
      {icon === "Deforestation" && <GiTreeDoor className="text-green-500" />}
    </g>
  );
};

export default ImpactChart;
