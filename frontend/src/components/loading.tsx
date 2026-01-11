import React from "react";
import { Ripple } from "@/components/magicui/ripple";

export default function Loading() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-background">
      <div className="relative flex h-[500px] w-full flex-col items-center justify-center overflow-hidden rounded-lg ">
        <p className="z-10 whitespace-pre-wrap text-center text-5xl font-medium tracking-tighter text-white">
          Loading
        </p>
        <Ripple />
      </div>
    </div>
  );
}
