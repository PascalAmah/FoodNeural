import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  RadialBarChart,
  RadialBar,
} from "recharts";
import { motion as Motion } from "framer-motion";
import { GiWaterDrop } from "react-icons/gi";

const ImpactChart = ({ impactData }) => {
  if (!impactData) return null;

  // Data for bar chart (excluding water)
  const barData = [
    {
      name: "Carbon (kg CO₂)",
      value: impactData.carbon,
    },
    {
      name: "Energy (kWh)",
      value: impactData.energy,
    },
    {
      name: "Waste (kg)",
      value: impactData.waste,
    },
    {
      name: "Deforestation (ha)",
      value: impactData.deforestation || 0,
    },
  ];

  // Data for water (radial bar chart)
  const waterData = [
    { name: "Water (L)", value: impactData.water, fill: "#60a5fa" },
  ];

  // Data for pie chart (impact distribution, including water)
  const totalImpact =
    impactData.carbon +
    impactData.water +
    impactData.energy +
    impactData.waste +
    (impactData.deforestation || 0);

  const COLORS = {
    Carbon: "#ff6b6b", // Red for high impact
    Water: "#60a5fa", // Blue for water
    Energy: "#feca57", // Yellow for medium impact
    Waste: "#1dd1a1", // Green for low impact
    Deforestation: "#ff9f43", // Orange for deforestation
  };

  const pieData = [
    {
      name: "Carbon",
      value: totalImpact > 0 ? (impactData.carbon / totalImpact) * 100 : 0,
      color: COLORS.Carbon,
    },
    {
      name: "Water",
      value: totalImpact > 0 ? (impactData.water / totalImpact) * 100 : 0,
      color: COLORS.Water,
    },
    {
      name: "Energy",
      value: totalImpact > 0 ? (impactData.energy / totalImpact) * 100 : 0,
      color: COLORS.Energy,
    },
    {
      name: "Waste",
      value: totalImpact > 0 ? (impactData.waste / totalImpact) * 100 : 0,
      color: COLORS.Waste,
    },
    {
      name: "Deforestation",
      value:
        totalImpact > 0
          ? ((impactData.deforestation || 0) / totalImpact) * 100
          : 0,
      color: COLORS.Deforestation,
    },
  ];

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
      className="bg-white md:p-6 md:rounded-xl md:shadow-lg"
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
        <div className="flex flex-col md:flex-row items-center gap-4">
          <ResponsiveContainer width="70%" height={250}>
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="50%"
              outerRadius="90%"
              barSize={25}
              data={waterData}
            >
              <RadialBar
                minAngle={15}
                background
                clockWise
                dataKey="value"
                cornerRadius={12}
              >
                {waterData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </RadialBar>
              <Tooltip formatter={(value) => `${value.toLocaleString()} L`} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="text-blue-600 font-medium text-lg">
            {impactData.water.toLocaleString()} L
          </div>
        </div>
      </div>

      {/* Bar Chart Section (Impact Metrics) */}
      <div className="mb-8">
        <h4 className="text-md font-medium text-gray-700 mb-2">
          Impact Metrics
        </h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={barData}
            margin={{ top: 20, right: 30, left: 20, bottom: 50 }}
          >
            <XAxis
              dataKey="name"
              tick={<CustomizedAxisTick fontSize={12} />}
              interval={0}
              height={60}
            />
            <YAxis fontSize={12} />
            <Tooltip />
            <Bar dataKey="value" fill={getBarColor()} radius={[4, 4, 0, 0]}>
              {barData.map((entry) => (
                <Cell
                  key={`cell-${entry.name}`}
                  fill={COLORS[entry.name.split(" ")[0]]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <ImpactLevelIndicator />
      </div>

      {/* Impact Distribution Section */}
      <div>
        <h4 className="text-md font-medium text-gray-700 mb-2">
          Impact Distribution
        </h4>
        <ImpactDistributionText pieData={pieData} />
      </div>
    </Motion.div>
  );
};

const CustomizedAxisTick = ({ x, y, payload, fontSize }) => {
  return (
    <g transform={`translate(${x},${y})`}>
      <text
        x={0}
        y={0}
        dy={16}
        textAnchor="end"
        fill="#666"
        transform="rotate(-35)"
        style={{ fontSize }}
      >
        {payload.value}
      </text>
    </g>
  );
};

const ImpactDistributionText = ({ pieData }) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
    {pieData.map((item) => (
      <div key={item.name} className="flex items-center gap-2">
        <div
          className="w-4 h-4 rounded-full"
          style={{ backgroundColor: item.color }}
        />
        <span className="text-gray-700">
          {item.name}: <strong>{item.value.toFixed(1)}%</strong>
        </span>
      </div>
    ))}
  </div>
);

const ImpactLevelIndicator = () => (
  <div className="flex flex-wrap gap-4 justify-center mt-4 text-xs md:text-sm">
    <div className="flex items-center gap-2">
      <div className="w-4 h-4 rounded-full bg-red-400" />
      <span className="text-sm text-gray-600">High Impact</span>
    </div>
    <div className="flex items-center gap-2">
      <div className="w-4 h-4 rounded-full bg-yellow-400" />
      <span className="text-sm text-gray-600">Medium Impact</span>
    </div>
    <div className="flex items-center gap-2">
      <div className="w-4 h-4 rounded-full bg-green-400" />
      <span className="text-sm text-gray-600">Low Impact</span>
    </div>
    <div className="flex items-center gap-2">
      <div className="w-4 h-4 rounded-full bg-gray-400" />
      <span className="text-sm text-gray-600">Default</span>
    </div>
  </div>
);

export default ImpactChart;
