"use client";

import { motion } from "framer-motion";
import { Code, Smile, Atom, Shield } from "lucide-react";

export default function BenefitsSection() {
  return (
    <section className="w-full py-16 md:py-24 dark:text-white ">
      <div className="container px-4 md:px-6 mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl font-bold tracking-tighter text-[#126ed3] sm:text-5xl md:text-6xl">
            Benefits of clean code
          </h2>
        </motion.div>

        <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-4">
          <motion.div
            className="flex flex-col space-y-4"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            viewport={{ once: true }}
          >
            <div className="relative h-20 w-20 dark:text-white">
              <div className="absolute inset-0 rounded-md bg-red-600"></div>
              <div className="absolute inset-0 -translate-x-2 -translate-y-2 rounded-md border-2 border-purple-900 bg-white p-3">
                <Code className="h-10 w-10 text-purple-900 self-center" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-[#126ed3] dark:text-[#126ed3]">
              Cleaner code, lower maintenance.
            </h3>
            <p className="text-gray-700 dark:text-white">
              Clean Code is easier to read, reuse, and enhance, keeping
              maintenance time and costs to a minimum. Create well-organized
              scalable, reliable, and testable software that improves code
              quality.
            </p>
          </motion.div>

          <motion.div
            className="flex flex-col space-y-4"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            viewport={{ once: true }}
          >
            <div className="relative h-20 w-20">
              <div className="absolute inset-0 rounded-md bg-red-600"></div>
              <div className="absolute inset-0 -translate-x-2 -translate-y-2 rounded-md border-2 border-purple-900 bg-white p-3">
                <Smile className="h-10 w-10 text-purple-900" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-[#126ed3] dark:text-[#126ed3]">
              Keep your developers happy.
            </h3>
            <p className="text-gray-700 dark:text-white">
              By keeping the most essential piece of your workplace—your
              code—clean, you create an enjoyable and satisfactory work
              environment for everyone. Clean Code is modular, easy to
              understand, and modifiable; helping improve developer
              collaboration.
            </p>
          </motion.div>

          <motion.div
            className="flex flex-col space-y-4"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            viewport={{ once: true }}
          >
            <div className="relative h-20 w-20">
              <div className="absolute inset-0 rounded-md bg-red-600"></div>
              <div className="absolute inset-0 -translate-x-2 -translate-y-2 rounded-md border-2 border-purple-900 bg-white p-3">
                <Atom className="h-10 w-10 text-purple-900" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-[#126ed3] dark:text-[#126ed3]">
              Rework less, innovate more.
            </h3>
            <p className="text-gray-700 dark:text-white">
              Generate greater business value by empowering developers to focus
              on solving interesting problems instead of spending time on
              remediating old problems. Clean Code improves software quality and
              increases productivity, so you can deliver more features.
            </p>
          </motion.div>

          <motion.div
            className="flex flex-col space-y-4"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            viewport={{ once: true }}
          >
            <div className="relative h-20 w-20">
              <div className="absolute inset-0 rounded-md bg-red-600"></div>
              <div className="absolute inset-0 -translate-x-2 -translate-y-2 rounded-md border-2 border-purple-900 bg-white p-3">
                <Shield className="h-10 w-10 text-purple-900" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-[#126ed3] dark:text-[#126ed3]">
              Minimize risks, maximize reputation.
            </h3>
            <p className="text-gray-700 dark:text-white">
              Sonar keeps your software robust and secure with the right checks
              at the right place and time. Limit the risk of introducing
              security vulnerabilities during the agile development process with
              code reviews.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
