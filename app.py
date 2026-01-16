import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# Page configuration (must be first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    page_title="AI Fitness Planner",
    layout="centered"
)

# --------------------------------------------------
# Load datasets
# --------------------------------------------------
diet_df = pd.read_csv("diet_data.csv")
workout_df = pd.read_csv("workout_data.csv")

# --------------------------------------------------
# Initialize variables (FIXES NameError)
# --------------------------------------------------
diet_plan = pd.DataFrame()
workout_plan = pd.DataFrame()

# --------------------------------------------------
# Title
# --------------------------------------------------
st.title("🏋️ Personalized Workout & Diet Planner (AI)")
st.write("Student-focused • Budget-friendly • With workout videos")

# --------------------------------------------------
# User Inputs
# --------------------------------------------------
st.header("👤 Enter Your Details")

age = st.slider("Age", 16, 40, 21)
gender = st.selectbox("Gender", ["Male", "Female"])
height = st.number_input("Height (cm)", 140, 210, 170)
weight = st.number_input("Weight (kg)", 40, 130, 65)

goal = st.selectbox("Fitness Goal", ["weight_loss", "muscle_gain", "maintenance"])
diet_type = st.selectbox("Diet Preference", ["veg", "non-veg"])
budget = st.selectbox("Food Budget", ["low", "medium"])
equipment = st.selectbox("Workout Equipment", ["none", "gym"])
activity = st.selectbox(
    "Activity Level",
    ["Sedentary", "Light", "Moderate", "Active"]
)

# --------------------------------------------------
# Health Calculations
# --------------------------------------------------
height_m = height / 100
bmi = weight / (height_m ** 2)

# WHO BMI classification
if bmi < 18.5:
    bmi_status = "Underweight"
elif bmi < 25:
    bmi_status = "Normal"
elif bmi < 30:
    bmi_status = "Overweight"
else:
    bmi_status = "Obese"

# BMR – Mifflin-St Jeor Equation (NIH)
if gender == "Male":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

activity_factor = {
    "Sedentary": 1.2,
    "Light": 1.375,
    "Moderate": 1.55,
    "Active": 1.725
}

tdee = bmr * activity_factor[activity]

if goal == "weight_loss":
    calorie_target = tdee - 400
elif goal == "muscle_gain":
    calorie_target = tdee + 300
else:
    calorie_target = tdee

# --------------------------------------------------
# Generate Plan Button
# --------------------------------------------------
if st.button("🚀 Generate My AI Fitness Plan"):

    # ------------------------------
    # Health Summary
    # ------------------------------
    st.subheader("📊 Health Summary")
    st.write(f"**BMI:** {bmi:.2f} ({bmi_status})")
    st.write(f"**BMR:** {int(bmr)} kcal/day")
    st.write(f"**Daily Calorie Target:** {int(calorie_target)} kcal")

    # ------------------------------
    # BMI Visualization
    # ------------------------------
    st.subheader("📈 BMI Visualization")

    bmi_categories = ["Underweight", "Normal", "Overweight", "Obese"]
    bmi_reference = [18.5, 24.9, 29.9, 35]

    fig, ax = plt.subplots()
    ax.bar(bmi_categories, bmi_reference)
    ax.axhline(bmi, linestyle="--")
    ax.set_ylabel("BMI Value")
    ax.set_title("BMI Category Reference (WHO)")
    st.pyplot(fig)

    # ------------------------------
    # Diet Recommendation
    # ------------------------------
    st.subheader("🥗 Personalized Diet Plan")

    diet_plan = diet_df[
        (diet_df["diet_type"] == diet_type) &
        (diet_df["cost"] == budget) &
        (diet_df["calories"] <= calorie_target / 3)
    ].head(3)

    if diet_plan.empty:
        st.warning("No matching diet found.")
    else:
        meals = ["Breakfast", "Lunch", "Dinner"]
        diet_plan = diet_plan.copy()
        diet_plan["Meal"] = meals[:len(diet_plan)]
        st.dataframe(diet_plan[["Meal", "food", "calories", "protein"]])

    # ------------------------------
    # Workout Recommendation + Videos
    # ------------------------------
    st.subheader("🏃 Personalized Workout Plan (With Videos)")

    workout_plan = workout_df[
        (workout_df["goal"] == goal) &
        (workout_df["equipment"] == equipment)
    ]

    if workout_plan.empty:
        st.warning("No matching workout found.")
    else:
        for _, row in workout_plan.iterrows():
            st.markdown(f"### 💪 {row['exercise']}")
            st.write(f"⏱ Duration: {row['duration_min']} min")
            st.write(f"🔥 Calories Burned: {row['calories_burned']} kcal")
            st.video(row["video_url"])

    # ------------------------------
    # Weekly Workout Schedule
    # ------------------------------
    if not workout_plan.empty:
        st.subheader("🗓 Weekly Workout Schedule")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        weekly_plan = workout_plan.sample(len(days), replace=True).copy()
        weekly_plan["Day"] = days
        st.dataframe(weekly_plan[["Day", "exercise", "duration_min"]])

    # ------------------------------
    # Calories Intake vs Burn
    # ------------------------------
    if not diet_plan.empty and not workout_plan.empty:
        st.subheader("⚖ Calories Intake vs Burn")

        intake = diet_plan["calories"].sum()
        burn = workout_plan["calories_burned"].sum()

        fig2, ax2 = plt.subplots()
        ax2.bar(["Intake", "Burn"], [intake, burn])
        ax2.set_ylabel("Calories")
        ax2.set_title("Calories Comparison")
        st.pyplot(fig2)

    # ------------------------------
    # AI Health Advice
    # ------------------------------
    st.subheader("🧠 AI Health Advice")

    if bmi_status == "Underweight":
        st.info("Increase calories with protein-rich foods and strength training.")
    elif bmi_status == "Normal":
        st.success("Maintain balanced diet and regular exercise.")
    elif bmi_status == "Overweight":
        st.warning("Focus on calorie deficit and cardio workouts.")
    else:
        st.error("Consult a healthcare professional before intense workouts.")

    # ------------------------------
    # Download Plan
    # ------------------------------
    st.subheader("💾 Download Your Fitness Plan")

    final_plan = pd.concat([diet_plan, workout_plan], axis=0)
    csv = final_plan.to_csv(index=False)

    st.download_button(
        label="Download Plan as CSV",
        data=csv,
        file_name="my_ai_fitness_plan.csv",
        mime="text/csv"
    )

    st.success("✅ Your complete AI fitness plan is ready!")